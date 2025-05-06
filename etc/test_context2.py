import os
import glob
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Função para carregar e processar o conhecimento
def inicializar_rag(diretorio_rag: str = r'.\RAG') -> tuple[list, faiss.IndexFlatL2]:
    """Inicializa o modelo de embeddings, documentos e índice FAISS a partir dos arquivos de capítulo."""
    # Inicializa o modelo SentenceTransformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Padrão para arquivos como b1.txt, b2.txt, ..., s1.txt, ..., d1.txt, ..., e1.txt
    padrao_arquivos = os.path.join(diretorio_rag, '[bsde][1-9].txt')
    caminhos_arquivos = glob.glob(padrao_arquivos)
    
    if not caminhos_arquivos:
        raise ValueError(f"Nenhum arquivo encontrado em {diretorio_rag}.")
    
    documentos = []
    # Carrega e processa cada arquivo de capítulo
    for caminho in caminhos_arquivos:
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read().split('\n\n')
                documentos.extend([doc.strip() for doc in conteudo if doc.strip()])
        else:
            print(f"Arquivo não encontrado: {caminho}")
    
    if not documentos:
        raise ValueError("Nenhum documento foi carregado. Verifique os caminhos dos arquivos.")
    
    print(f"Carregados {len(documentos)} documentos.")
    
    # Gera embeddings usando o SentenceTransformer
    embeddings = []
    batch_size = 32  # Processa em lotes para maior eficiência
    for i in range(0, len(documentos), batch_size):
        batch = documentos[i:i + batch_size]
        print(f"Gerando embeddings {i}/{len(documentos)}...")
        try:
            batch_embeddings = embedder.encode(batch, show_progress_bar=False)
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Erro ao gerar embeddings para lote {i}: {e}")
            embeddings.extend([np.zeros(384) for _ in batch])  # Dimensão do all-MiniLM-L6-v2 é 384
    
    print(f"Gerados {len(embeddings)} embeddings.")
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Cria o índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    return documentos, index, embedder

# Função para buscar contexto relevante
def buscar_contexto(pergunta: str, documentos: list, index: faiss.IndexFlatL2, embedder: SentenceTransformer, k: int = 5) -> list:
    """Busca os k documentos mais relevantes para a pergunta."""
    try:
        query_embedding = embedder.encode([pergunta], show_progress_bar=False)
        query_embedding = np.array(query_embedding, dtype=np.float32)
        
        # Busca no índice FAISS
        D, I = index.search(query_embedding, k)
        return [(i, documentos[i], D[0][j]) for j, i in enumerate(I[0])]
    except Exception as e:
        print(f"Erro ao buscar contexto: {e}")
        return []

# Função para testar a recuperação de contexto
def testar_contexto():
    """Permite inserir uma frase e retorna os contextos mais relevantes."""
    print("Inicializando RAG...")
    try:
        documentos, index, embedder = inicializar_rag()
    except Exception as e:
        print(f"Erro ao inicializar RAG: {e}")
        return
    
    while True:
        frase = input("\nDigite uma frase (ou 'sair' para encerrar): ")
        if frase.lower() == 'sair':
            break
        
        print(f"\nBuscando contexto para: '{frase}'")
        contextos = buscar_contexto(frase, documentos, index, embedder, k=5)
        
        if not contextos:
            print("Nenhum contexto encontrado.")
            continue
        
        print("\nContextos mais relevantes:")
        for idx, texto, distancia in contextos:
            print(f"\nÍndice: {idx}, Distância: {distancia:.4f}")
            print(f"Texto: {texto[:1600]}...")  # Limita a saída para facilitar leitura
            print("-" * 50)

# Executar o teste
if __name__ == "__main__":
    testar_contexto()