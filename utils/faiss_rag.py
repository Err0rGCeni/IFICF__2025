import os
import glob
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Configurações
RAG_DIR = r'.\RAG'
DATA_DIR = os.path.join(RAG_DIR, 'data')
FAISS_DIR = os.path.join(RAG_DIR, 'FAISS')
CONTEXT_FAISS_PATH = os.path.join(FAISS_DIR, 'context_index.faiss')
CONTEXT_JSON_PATH = os.path.join(FAISS_DIR, 'context_texts.json')
MODEL_NAME = 'nomic-ai/nomic-embed-text-v2-moe'

def inicializar_rag(diretorio_rag: str = RAG_DIR) -> tuple[list, faiss.IndexFlatL2, SentenceTransformer]:
    """Inicializa o modelo de embeddings, documentos e índice FAISS."""
    # Criar pasta FAISS se não existir
    os.makedirs(FAISS_DIR, exist_ok=True)

    # Verificar se os arquivos .faiss e .json já existem
    if os.path.exists(CONTEXT_FAISS_PATH) and os.path.exists(CONTEXT_JSON_PATH):
        print("Carregando índice e documentos existentes...")
        index = faiss.read_index(CONTEXT_FAISS_PATH)
        with open(CONTEXT_JSON_PATH, 'r', encoding='utf-8') as f:
            documentos = json.load(f)
        embedder = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
        print(f"Carregados {len(documentos)} documentos do índice existente.")
        return documentos, index, embedder

    # Inicializar o modelo SentenceTransformer
    embedder = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

    # Carregar arquivos
    padrao_arquivos = os.path.join(DATA_DIR, 'CF_[a-z].txt')
    caminhos_arquivos = glob.glob(padrao_arquivos)

    if not caminhos_arquivos:
        raise ValueError(f"Nenhum arquivo encontrado em {diretorio_rag}.")

    documentos = []
    for caminho in caminhos_arquivos:
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read().split('\n\n')
                documentos.extend([doc.strip() for doc in conteudo if doc.strip()])
        else:
            print(f"Arquivo não encontrado: {caminho}")

    if not documentos:
        raise ValueError("Nenhum documento foi carregado.")

    print(f"Carregados {len(documentos)} documentos.")

    # Gerar embeddings
    embeddings = []
    batch_size = 32
    for i in range(0, len(documentos), batch_size):
        batch = documentos[i:i + batch_size]
        try:
            batch_embeddings = embedder.encode(batch, show_progress_bar=True)
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Erro ao gerar embeddings para lote {i}: {e}")
            embeddings.extend([np.zeros(768) for _ in batch])  # Ajustar dimensão conforme o modelo

    print(f"Gerados {len(embeddings)} embeddings.")
    embeddings = np.array(embeddings, dtype=np.float32)

    # Criar índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Salvar índice e documentos
    faiss.write_index(index, CONTEXT_FAISS_PATH)
    with open(CONTEXT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(documentos, f, ensure_ascii=False)
    print(f"Índice e documentos salvos em {FAISS_DIR}.")

    return documentos, index, embedder

def buscar_contexto(pergunta: str, documentos: list, index: faiss.IndexFlatL2, embedder: SentenceTransformer, k: int = 3) -> list:
    """Busca os k documentos mais relevantes para a pergunta."""
    try:
        query_embedding = embedder.encode([pergunta], show_progress_bar=False)
        query_embedding = np.array(query_embedding, dtype=np.float32)
        D, I = index.search(query_embedding, k)
        return [(i, documentos[i], D[0][j]) for j, i in enumerate(I[0])]
    except Exception as e:
        print(f"Erro ao buscar contexto: {e}")
        return []

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
            print(f"Texto: {texto[:1600]}...")
            print("-" * 50)

if __name__ == "__main__":
    testar_contexto()