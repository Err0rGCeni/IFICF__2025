import ollama
import faiss
import gradio as gr
import numpy as np
import os
import glob

print("Inicializando...")

# Função para carregar e processar o conhecimento
def inicializar_rag():
    """Inicializa o modelo de embeddings, documentos e índice FAISS a partir dos arquivos de capítulo."""
    # Diretório onde os arquivos de capítulo estão localizados
    diretorio_rag = r'.\RAG'
    
    # Padrão para encontrar arquivos como b1.txt, b2.txt, ..., s1.txt, ..., d1.txt, ..., e1.txt, etc.
    padrao_arquivos = os.path.join(diretorio_rag, '[bsde][1-9].txt')
    caminhos_arquivos = glob.glob(padrao_arquivos)
    
    documentos = []
    # Carrega e processa cada arquivo de capítulo
    for caminho in caminhos_arquivos:
        if os.path.exists(caminho):            
            with open(caminho, 'r', encoding='utf-8') as f:
                # Divide em parágrafos (mantendo o separador original do código)
                conteudo = f.read().split('\n\n')
                documentos.extend(conteudo)
        else:
            print(f"Arquivo não encontrado: {caminho}")
    
    if not documentos:
        raise ValueError("Nenhum documento foi carregado. Verifique os caminhos dos arquivos.")
    
    print(f"Trabalhando em {len(documentos)} documentos ...")
    # Gera embeddings usando o Ollama
    embeddings = []
    for index, doc in enumerate(documentos):
        if index % 200 == 0:
            print(f"= = = {index} Embeddings... = = =")
        # nomic-embed-text é um modelo para parágrafos mais longos
        response = ollama.embed(model="nomic-embed-text", input=doc)
        if index % 200 == 0:
            print(f"Response: {response}")
        embeddings.append(response['embeddings'][0])  # Acessa o embedding gerado
    print(f"Trabalhando em {len(embeddings)} embeddings...")
    embeddings = np.array(embeddings, dtype=np.float32)  # Converte para numpy array
    
    # Cria o índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return documentos, index

# Função para buscar contexto relevante
def buscar_contexto(pergunta, documentos, index, k=5):
    """Busca os k documentos mais relevantes para a pergunta."""
    # Gera embedding para a pergunta usando o Ollama
    response = ollama.embed(model="nomic-embed-text", input=pergunta)
    query_embedding = np.array([response['embeddings'][0]], dtype=np.float32)
    
    # Busca no índice FAISS
    D, I = index.search(query_embedding, k)
    return [documentos[i] for i in I[0]]

# Função para gerar resposta com o Ollama
def gerar_resposta(frase_entrada, documentos, index):
    """Gera uma resposta baseada no contexto recuperado."""
    contexto = buscar_contexto(frase_entrada, documentos, index)
    contexto_str = "\n".join(contexto)
    
    # Prompt com instruções detalhadas sobre CIF
    prompt = f"""
        1. Identifique o **conceito significativo** da frase "XXXXXX", ou seja, o propósito ou a ideia central que ela expressa, independentemente de ser uma pergunta ou uma afirmação. 
        2. Para determinar a vinculação de um termo específico com a Classificação Internacional de Funcionalidade (CIF), segundo Cieza et al., 2016, siga as diretrizes a seguir: 
        3. Identifique se o termo pertence ao universo da CIF, de acordo com o documento anexado: 
        - Se o termo é mencionado no arquivo anexado, anote isso. 
        - Se o termo não aparece no arquivo anexado, classifique como "Não coberto."
        4. Verifique a relação do termo com os componentes da CIF: 
        - Funções Corporais: Se o termo se relaciona com códigos iniciados pela letra “b”
        - Estruturas Corporais: Se o termo se relaciona com códigos iniciados pela letra “s” 
        - Atividades e Participação: Se o termo se relaciona com códigos iniciados pela letra “d” 
        - Fatores Ambientais: Se o termo se relaciona com códigos iniciados pela letra “e”
        5. Classifique o termo: Se o termo for mencionado na CIF e tiver vínculo com um dos componentes acima, identifique qual categoria ele pertence. 
        Se o termo for mencionado na CIF, mas não tiver vínculo com nenhuma das categorias existentes, classifique como "Não Definido." 

        **RAG**:
        {contexto_str}

        **Frase**:  
        {frase_entrada}

        **Formato da Resposta**:  
        - **Conceito**: [Descrição do conceito significativo]
        - **Código CIF**: [Código CIF + nomeclatura]
        - **Justificativa**: [Explicação baseada no RAG]
    """
    resposta = ollama.generate(model='gemma3:1b', prompt=prompt)
    return resposta['response']

# Função principal para a interface Gradio
def interface_rag(frase_entrada):
    """Função chamada pela interface Gradio."""
    resposta = gerar_resposta(frase_entrada, documentos, index)
    return resposta

# Inicialização do RAG
print("Inicializando RAG...")
documentos, index = inicializar_rag()

# Configuração da interface Gradio
interface = gr.Interface(
    fn=interface_rag,
    inputs=gr.Textbox(label="Digite sua frase", placeholder="Ex.: O que é função puberal?"),
    outputs=gr.Textbox(label="Resposta"),
    title="Sistema RAG para CIF",
    description="Pergunte algo sobre Funções Corporais, Estruturas Corporais, Atividades e Participação ou Fatores Ambientais com base na CIF."
)

# Iniciar a interface
print("Gerando Interface...")
interface.launch()
