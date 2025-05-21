import os
import glob
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from nltk import sent_tokenize
import nltk

# Baixar o tokenizador de frases do NLTK (necessário apenas uma vez)
try:
    nltk.data.find('tokenizers/punkt') or nltk.download('tokenizers/punkt_tab')
except nltk.downloader.DownloadError:
    nltk.download('punkt_tab')

# Configurações
RAG_DIR = r'.\RAG'
DATA_DIR = os.path.join(RAG_DIR, 'data')
FAISS_DIR = os.path.join(RAG_DIR, 'FAISS')
CONTEXT_FAISS_PATH = os.path.join(FAISS_DIR, 'context_index.faiss')
CONTEXT_JSON_PATH = os.path.join(FAISS_DIR, 'context_texts.json')
MODEL_NAME = 'nomic-ai/nomic-embed-text-v2-moe'

def carregar_embedder() -> SentenceTransformer:
    """
    Inicializa e carrega o modelo de embedding SentenceTransformer especificado.

    Este modelo é usado para converter texto em vetores numéricos (embeddings),
    que são essenciais para a busca de similaridade no índice FAISS.

    Returns:
        SentenceTransformer: Uma instância do modelo SentenceTransformer carregado.
    """
    print(f"Carregando modelo de embeddings {MODEL_NAME}...")
    return SentenceTransformer(MODEL_NAME, trust_remote_code=True)

def carregar_indices_existentes() -> tuple[list | None, faiss.Index | None]:
    """
    Tenta carregar um índice FAISS e os documentos de texto associados
    se os arquivos de índice e JSON já existirem no diretório FAISS_DIR.

    Esta função verifica a persistência para evitar a recriação custosa
    do índice a cada inicialização, se os dados subjacentes não mudaram.

    Returns:
        tuple[list | None, faiss.Index | None]: Uma tupla contendo a lista de documentos
                                                 e o objeto do índice FAISS se ambos forem
                                                 carregados com sucesso. Caso contrário,
                                                 retorna (None, None).
    """
    if os.path.exists(CONTEXT_FAISS_PATH) and os.path.exists(CONTEXT_JSON_PATH):
        print("Carregando índice e documentos existentes...")
        try:
            index = faiss.read_index(CONTEXT_FAISS_PATH)
            with open(CONTEXT_JSON_PATH, 'r', encoding='utf-8') as f:
                documentos = json.load(f)
            print(f"Carregados {len(documentos)} documentos do índice existente.")
            return documentos, index
        except Exception as e:
            print(f"Erro ao carregar índice ou documentos existentes: {e}. Reconstruindo.")
            return None, None
    return None, None

def carregar_documentos() -> list[str]:
    """
    Carrega e pré-processa documentos de texto da pasta de dados (DATA_DIR).

    Esta função busca todos os arquivos '.txt' no diretório especificado,
    lê seus conteúdos e os divide em unidades de contexto (parágrafos ou blocos
    separados por linhas em branco duplas). Linhas vazias são filtradas.

    Returns:
        list[str]: Uma lista de strings, onde cada string é uma unidade de contexto
                   extraída dos documentos.

    Raises:
        ValueError: Se nenhum arquivo '.txt' for encontrado no diretório de dados
                    ou se nenhum documento válido for carregado após o processamento.
    """
    caminhos_arquivos = glob.glob(os.path.join(DATA_DIR, '*.txt'))
    if not caminhos_arquivos:
        raise ValueError(f"Nenhum arquivo .txt encontrado em {DATA_DIR}. Por favor, adicione documentos.")

    documentos = []
    for caminho in caminhos_arquivos:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                documentos.extend(list(filter(None, map(str.strip, f.read().split('\n\n')))))
        except Exception as e:
            print(f"Erro ao ler o arquivo {caminho}: {e}")
            continue
    
    if not documentos:
        raise ValueError("Nenhum documento válido foi carregado após o processamento dos arquivos.")

    print(f"Carregados {len(documentos)} documentos.")
    return documentos

def gerar_embeddings(embedder: SentenceTransformer, documentos: list[str]) -> np.ndarray:
    """
    Gera embeddings numéricos para uma lista de documentos de texto usando o embedder fornecido.

    Os embeddings são representações vetoriais de texto que capturam seu significado semântico,
    permitindo a comparação de similaridade.

    Args:
        embedder (SentenceTransformer): O modelo de embedding previamente carregado.
        documentos (list[str]): A lista de strings de texto para as quais gerar embeddings.

    Returns:
        np.ndarray: Um array NumPy de tipo float32 contendo os embeddings gerados.
                    Cada linha do array corresponde ao embedding de um documento.

    Raises:
        ValueError: Se nenhum embedding puder ser gerado (ex: lista de documentos vazia).
    """
    print("Gerando embeddings para os documentos...")
    batch_size = 32
    embeddings_list = []
    for i in range(0, len(documentos), batch_size):
        batch = documentos[i:i + batch_size]
        try:
            if batch: # Garante que o lote não está vazio
                embeddings_list.extend(embedder.encode(batch, show_progress_bar=False))
        except Exception as e:
            print(f"Erro ao gerar embeddings para lote {i}: {e}")
            # Em caso de erro, preenche com vetores de zeros do tamanho correto
            embeddings_list.extend([np.zeros(embedder.get_sentence_embedding_dimension()) for _ in batch])

    if not embeddings_list:
        raise ValueError("Nenhum embedding foi gerado.")

    return np.array(embeddings_list, dtype=np.float32)

def criar_indice_faiss(embeddings: np.ndarray) -> faiss.Index:
    """
    Cria e popula um índice FAISS (Facebook AI Similarity Search) a partir de um conjunto de embeddings.

    O índice FAISS é uma estrutura de dados otimizada para realizar buscas de similaridade
    eficientes em grandes coleções de vetores.

    Args:
        embeddings (np.ndarray): Um array NumPy contendo os embeddings dos documentos.

    Returns:
        faiss.Index: O objeto do índice FAISS populado, pronto para buscas.
    """
    print("Criando índice FAISS...")
    dimension = embeddings.shape[1]
    # IndexFlatL2 usa a distância euclidiana (L2) para similaridade.
    # Distâncias menores indicam maior similaridade.
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def inicializar_rag() -> tuple[list[str], faiss.Index, SentenceTransformer]:
    """
    Inicializa o sistema RAG (Retrieval Augmented Generation) completo.

    Este processo envolve:
    1. Criar diretórios necessários para persistência.
    2. Carregar o modelo de embedding.
    3. Tentar carregar um índice FAISS e documentos existentes.
    4. Se não existirem ou estiverem corrompidos, carregar documentos do disco,
       gerar seus embeddings, criar um novo índice FAISS e salvá-los para uso futuro.

    Returns:
        tuple[list[str], faiss.Index, SentenceTransformer]: Uma tupla contendo:
                                                            - A lista de documentos de texto.
                                                            - O objeto do índice FAISS.
                                                            - O modelo SentenceTransformer carregado.
    """
    print("Inicializando RAG...")
    os.makedirs(FAISS_DIR, exist_ok=True)
    embedder = carregar_embedder()
    documentos, index = carregar_indices_existentes()

    if index is None: # Se o índice não existe ou houve erro ao carregar, reconstrói
        print("Índice FAISS não encontrado ou corrompido. Reconstruindo...")
        documentos = carregar_documentos()
        embeddings = gerar_embeddings(embedder, documentos)
        index = criar_indice_faiss(embeddings)

        faiss.write_index(index, CONTEXT_FAISS_PATH)
        with open(CONTEXT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(documentos, f, ensure_ascii=False)
        print("Novo índice e documentos salvos com sucesso.")

    return documentos, index, embedder

def buscar_contexto_completo(pergunta: str, documentos: list[str], index: faiss.Index, embedder: SentenceTransformer, k: int = 3) -> list[tuple[int, str, float]]:
    """
    Busca os 'k' documentos mais relevantes para a **pergunta completa**,
    tratando-a como uma única unidade de busca. Esta função não segmenta a pergunta em frases.

    Args:
        pergunta (str): A pergunta completa do usuário.
        documentos (list[str]): Lista de strings, onde cada string é um documento de contexto.
        index (faiss.Index): O índice FAISS carregado, contendo os embeddings dos documentos.
        embedder (SentenceTransformer): O modelo de embeddings usado para codificar a pergunta.
        k (int, opcional): O número de documentos mais relevantes a serem retornados. Padrão é 3.

    Returns:
        list[tuple[int, str, float]]: Uma lista de tuplas, onde cada tupla contém:
                                       - O índice do documento original na lista `documentos`.
                                       - O texto do documento.
                                       - A distância de similaridade (quanto menor, mais similar).
                                     Retorna uma lista vazia se a pergunta estiver vazia ou ocorrer um erro.
    """
    if not pergunta or not pergunta.strip():
        print("Pergunta vazia. Não é possível buscar contexto completo.")
        return []

    print(f"Buscando contexto completo para: '{pergunta}'")
    try:
        query_embedding = np.array(embedder.encode([pergunta]), dtype=np.float32)
        D, I = index.search(query_embedding, k)

        resultados = []
        for j in range(len(I[0])):
            doc_idx = I[0][j]
            distancia = D[0][j]
            # Garante que o índice é válido antes de adicionar
            if 0 <= doc_idx < len(documentos):
                resultados.append((doc_idx, documentos[doc_idx], distancia))
        
        # Os resultados do FAISS já vêm ordenados por distância crescente (mais similar primeiro).
        return resultados

    except Exception as e:
        print(f"Erro ao buscar contexto completo: {e}")
        return []

def buscar_multiplos_contextos(pergunta: str, documentos: list[str], index: faiss.Index, embedder: SentenceTransformer, k_por_frase: int = 2) -> list[tuple[int, str, float]]:
    """
    Segmenta a pergunta em frases e busca os 'k_por_frase' documentos mais relevantes
    para **CADA frase**, consolidando e retornando apenas contextos únicos.
    Se um documento é relevante para múltiplas frases, a menor distância (melhor relevância) é mantida.

    Args:
        pergunta (str): A pergunta do usuário, que pode conter múltiplas frases.
        documentos (list[str]): Lista de strings, onde cada string é um documento de contexto.
        index (faiss.Index): O índice FAISS carregado, contendo os embeddings dos documentos.
        embedder (SentenceTransformer): O modelo de embeddings usado para codificar as frases.
        k_por_frase (int, opcional): O número de documentos a buscar para cada frase da pergunta. Padrão é 2.

    Returns:
        list[tuple[int, str, float]]: Uma lista de tuplas (índice_documento, texto_documento, distancia)
                                     com os contextos únicos mais relevantes, ordenados pela distância
                                     (do mais relevante para o menos). Retorna uma lista vazia
                                     se a pergunta estiver vazia ou nenhuma frase for detectada.
    """
    if not pergunta or not pergunta.strip():
        print("Pergunta vazia. Não é possível buscar múltiplos contextos.")
        return []

    print(f"Buscando múltiplos contextos para: '{pergunta}'")
    
    frases = sent_tokenize(pergunta, language='portuguese')
    if not frases:
        print("Nenhuma frase detectada na pergunta para busca de múltiplos contextos.")
        return []
    
    # Dicionário para armazenar o melhor resultado para cada documento único:
    # {indice_documento: (indice_documento, texto, distancia)}
    # Isso garante unicidade e que a menor distância (melhor relevância) seja mantida.
    contextos_consolidados = {}
    
    try:
        for frase in frases:
            print(f"Processando frase para múltiplos contextos: '{frase}'")
            query_embedding = np.array(embedder.encode([frase]), dtype=np.float32)
            D, I = index.search(query_embedding, k_por_frase)
            
            for j in range(len(I[0])):
                doc_idx = I[0][j]
                distancia = D[0][j]
                
                if 0 <= doc_idx < len(documentos):
                    # Se o documento já foi encontrado, atualiza se a nova distância for menor (mais relevante)
                    if doc_idx not in contextos_consolidados or distancia < contextos_consolidados[doc_idx][2]:
                        contextos_consolidados[doc_idx] = (doc_idx, documentos[doc_idx], distancia)
        
        # Converte o dicionário de contextos consolidados de volta para uma lista
        resultados = list(contextos_consolidados.values())
        # Ordena os resultados finais pela distância (do mais relevante para o menos)
        resultados.sort(key=lambda x: x[2]) 
        
        return resultados

    except Exception as e:
        print(f"Erro ao buscar múltiplos contextos: {e}")
        return []

# --- Funções de Teste ---
def testar_busca_contexto():
    """
    Função de teste interativa para demonstrar as capacidades de busca de contexto.

    Permite que o usuário insira perguntas e escolha entre as estratégias
    'Buscar Contexto Completo' ou 'Buscar Múltiplos Contextos',
    exibindo os contextos mais relevantes encontrados.
    """
    try:
        documentos, index, embedder = inicializar_rag()
    except Exception as e:
        print(f"Erro ao inicializar RAG: {e}")
        return

    while True:
        pergunta = input("\nDigite uma pergunta (ou 'sair' para encerrar): ")
        if pergunta.lower() == 'sair':
            break

        print("\nEscolha o tipo de busca:")
        print("1. Buscar Contexto Completo")
        print("2. Buscar Múltiplos Contextos (segmentando a pergunta)")
        escolha = input("Opção (1 ou 2): ")

        contextos = []
        if escolha == '1':
            print(f"\nRealizando busca de contexto completo para: '{pergunta}'")
            contextos = buscar_contexto_completo(pergunta, documentos, index, embedder, k=5)
        elif escolha == '2':
            print(f"\nRealizando busca de múltiplos contextos para: '{pergunta}'")
            contextos = buscar_multiplos_contextos(pergunta, documentos, index, embedder, k_por_frase=3)
        else:
            print("Opção inválida. Tente novamente.")
            continue

        if not contextos:
            print("Nenhum contexto encontrado.")
            continue

        print("\nContextos mais relevantes:")
        for idx, texto, distancia in contextos:
            print(f"\nÍndice: {idx}, Distância: {distancia:.4f}")
            print(f"Texto: {texto[:500]}...") # Limita o texto para melhor visualização
            print("-" * 50)

if __name__ == "__main__":
    testar_busca_contexto()