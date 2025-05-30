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
# Configurações
RAG_DIR = r'.\RAG'
DATA_DIR = os.path.join(RAG_DIR, 'data')
FAISS_INDEX_DIR = os.path.join(RAG_DIR, 'FAISS') # Renamed from FAISS_DIR for clarity
CONTEXT_FAISS_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, 'context_index.faiss') # Renamed variable
CONTEXT_JSON_TEXT_PATH = os.path.join(FAISS_INDEX_DIR, 'context_texts.json') # Renamed variable
EMBEDDING_MODEL_NAME = 'nomic-ai/nomic-embed-text-v2-moe' # Renamed variable

def _load_embedding_model() -> SentenceTransformer:
    """
    Initializes and loads the specified SentenceTransformer embedding model.

    This model is used to convert text into numerical vectors (embeddings),
    which are essential for similarity search in the FAISS index.

    Returns:
        SentenceTransformer: An instance of the loaded SentenceTransformer model.
    """
    print(f"Carregando modelo de embeddings {EMBEDDING_MODEL_NAME}...")
    return SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)

def _load_existing_index_and_documents() -> tuple[list | None, faiss.Index | None]:
    """
    Attempts to load an existing FAISS index and its associated text documents
    if the index and JSON files already exist in the FAISS_INDEX_DIR.

    This function checks for persisted data to avoid costly recreation
    of the index with each initialization if the underlying data has not changed.

    Returns:
        tuple[list | None, faiss.Index | None]: A tuple containing the list of documents
                                                 and the FAISS index object if both are
                                                 successfully loaded. Otherwise,
                                                 returns (None, None).
    """
    if os.path.exists(CONTEXT_FAISS_INDEX_PATH) and os.path.exists(CONTEXT_JSON_TEXT_PATH):
        print("Carregando índice e documentos existentes...")
        try:
            faiss_index = faiss.read_index(CONTEXT_FAISS_INDEX_PATH)
            with open(CONTEXT_JSON_TEXT_PATH, 'r', encoding='utf-8') as f:
                loaded_documents = json.load(f)
            print(f"Carregados {len(loaded_documents)} documentos do índice existente.")
            return loaded_documents, faiss_index
        except Exception as e:
            print(f"Erro ao carregar índice ou documentos existentes: {e}. Reconstruindo.")
            return None, None
    return None, None

def _load_source_documents() -> list[str]:
    """
    Loads and preprocesses text documents from the data folder (DATA_DIR).

    This function searches for all '.txt' files in the specified directory,
    reads their contents, and splits them into context units (paragraphs or blocks
    separated by double blank lines). Empty lines are filtered out.

    Returns:
        list[str]: A list of strings, where each string is a context unit
                   extracted from the documents.

    Raises:
        ValueError: If no '.txt' files are found in the data directory
                    or if no valid documents are loaded after processing.
    """
    file_paths = glob.glob(os.path.join(DATA_DIR, '*.txt'))
    if not file_paths:
        raise ValueError(f"Nenhum arquivo .txt encontrado em {DATA_DIR}. Por favor, adicione documentos.")

    context_chunks = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Splits by double newline, strips whitespace, and filters out empty strings
                context_chunks.extend(list(filter(None, map(str.strip, f.read().split('\n\n')))))
        except Exception as e:
            print(f"Erro ao ler o arquivo {file_path}: {e}")
            continue

    if not context_chunks:
        raise ValueError("Nenhum documento válido foi carregado após o processamento dos arquivos.")

    print(f"Carregados {len(context_chunks)} documentos.")
    return context_chunks

def _generate_text_embeddings(embedder_model: SentenceTransformer, text_documents: list[str]) -> np.ndarray:
    """
    Generates numerical embeddings for a list of text documents using the provided embedder.

    Embeddings are vector representations of text that capture its semantic meaning,
    allowing for similarity comparison.

    Args:
        embedder_model (SentenceTransformer): The pre-loaded embedding model.
        text_documents (list[str]): The list of text strings for which to generate embeddings.

    Returns:
        np.ndarray: A NumPy array of type float32 containing the generated embeddings.
                    Each row in the array corresponds to the embedding of a document.

    Raises:
        ValueError: If no embeddings can be generated (e.g., empty document list).
    """
    print("Gerando embeddings para os documentos...")
    batch_size = 32
    generated_embeddings_list = []
    for i in range(0, len(text_documents), batch_size):
        batch = text_documents[i:i + batch_size]
        try:
            if batch: # Ensure the batch is not empty
                generated_embeddings_list.extend(embedder_model.encode(batch, show_progress_bar=False))
        except Exception as e:
            print(f"Erro ao gerar embeddings para lote {i//batch_size if batch_size > 0 else i}: {e}")
            # In case of error, fill with zero vectors of the correct dimension
            embedding_dim = embedder_model.get_sentence_embedding_dimension()
            generated_embeddings_list.extend([np.zeros(embedding_dim) for _ in batch])

    if not generated_embeddings_list:
        raise ValueError("Nenhum embedding foi gerado.")

    return np.array(generated_embeddings_list, dtype=np.float32)

def _create_faiss_index(document_embeddings: np.ndarray) -> faiss.Index:
    """
    Creates and populates a FAISS (Facebook AI Similarity Search) index from a set of embeddings.

    The FAISS index is a data structure optimized for performing efficient similarity searches
    in large collections of vectors.

    Args:
        document_embeddings (np.ndarray): A NumPy array containing the document embeddings.

    Returns:
        faiss.Index: The populated FAISS index object, ready for searches.
    """
    print("Criando índice FAISS...")
    dimension = document_embeddings.shape[1]
    # IndexFlatL2 uses Euclidean distance (L2) for similarity.
    # Smaller distances indicate greater similarity.
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(document_embeddings)
    return faiss_index

def initialize_rag_system() -> tuple[list[str], faiss.Index, SentenceTransformer]:
    """
    Initializes the complete RAG (Retrieval Augmented Generation) system.

    This process involves:
    1. Creating necessary directories for persistence.
    2. Loading the embedding model.
    3. Attempting to load an existing FAISS index and documents.
    4. If they don't exist or are corrupted, load documents from disk,
       generate their embeddings, create a new FAISS index, and save them for future use.

    Returns:
        tuple[list[str], faiss.Index, SentenceTransformer]: A tuple containing:
                                                             - The list of text documents.
                                                             - The FAISS index object.
                                                             - The loaded SentenceTransformer model.
    """
    print("Inicializando RAG...")
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    text_embedder = _load_embedding_model()
    context_documents, faiss_index = _load_existing_index_and_documents()

    if faiss_index is None: # If the index doesn't exist or an error occurred loading it, rebuild
        print("Índice FAISS não encontrado ou corrompido. Reconstruindo...")
        context_documents = _load_source_documents()
        document_embeddings = _generate_text_embeddings(text_embedder, context_documents)
        faiss_index = _create_faiss_index(document_embeddings)

        faiss.write_index(faiss_index, CONTEXT_FAISS_INDEX_PATH)
        with open(CONTEXT_JSON_TEXT_PATH, 'w', encoding='utf-8') as f:
            json.dump(context_documents, f, ensure_ascii=False, indent=4) # Added indent for readability
        print("Novo índice e documentos salvos com sucesso.")

    return context_documents, faiss_index, text_embedder

def search_with_full_query(full_question_text: str, context_documents: list[str], faiss_index: faiss.Index, embedder_model: SentenceTransformer, k_results: int = 3) -> list[tuple[int, str, float]]:
    """
    Searches for the 'k_results' most relevant documents for the **entire question**,
    treating it as a single search unit. This function does not segment the question into sentences.

    Args:
        full_question_text (str): The complete user question.
        context_documents (list[str]): List of strings, where each string is a context document.
        faiss_index (faiss.Index): The loaded FAISS index containing document embeddings.
        embedder_model (SentenceTransformer): The embedding model used to encode the question.
        k_results (int, optional): The number of most relevant documents to return. Defaults to 3.

    Returns:
        list[tuple[int, str, float]]: A list of tuples, where each tuple contains:
                                        - The original index of the document in `context_documents`.
                                        - The text of the document.
                                        - The similarity distance (lower means more similar).
                                      Returns an empty list if the question is empty or an error occurs.
    """
    if not full_question_text or not full_question_text.strip():
        print("Pergunta vazia. Não é possível buscar contexto completo.")
        return []

    print(f"Buscando contexto completo para: '{full_question_text}'")
    try:
        query_embedding = np.array(embedder_model.encode([full_question_text]), dtype=np.float32)
        # D: distances, I: indices of neighbors
        distances, indices = faiss_index.search(query_embedding, k_results)

        results_list = []
        for j in range(len(indices[0])):
            document_index = indices[0][j]
            distance_score = distances[0][j]
            # Ensure the index is valid before adding
            if 0 <= document_index < len(context_documents):
                results_list.append((document_index, context_documents[document_index], distance_score))

        # FAISS results are already sorted by increasing distance (most similar first).
        return results_list

    except Exception as e:
        print(f"Erro ao buscar contexto completo: {e}")
        return []

def search_with_multiple_sentences(question_text: str, context_documents: list[str], faiss_index: faiss.Index, embedder_model: SentenceTransformer, k_per_sentence: int = 2) -> list[tuple[int, str, float]]:
    """
    Segments the question into sentences and searches for the 'k_per_sentence' most relevant
    documents for **EACH sentence**, then consolidates and returns only unique contexts.
    If a document is relevant to multiple sentences, the lowest distance (best relevance) is kept.

    Args:
        question_text (str): The user question, which may contain multiple sentences.
        context_documents (list[str]): List of strings, where each string is a context document.
        faiss_index (faiss.Index): The loaded FAISS index containing document embeddings.
        embedder_model (SentenceTransformer): The embedding model used to encode sentences.
        k_per_sentence (int, optional): The number of documents to search for each sentence
                                     of the question. Defaults to 2.

    Returns:
        list[tuple[int, str, float]]: A list of tuples (document_index, document_text, distance)
                                      with the most relevant unique contexts, sorted by distance
                                      (most relevant to least relevant). Returns an empty list
                                      if the question is empty or no sentences are detected.
    """
    if not question_text or not question_text.strip():
        print("Pergunta vazia. Não é possível buscar múltiplos contextos.")
        return []

    print(f"Buscando múltiplos contextos para: '{question_text}'")

    sentences = sent_tokenize(question_text, language='portuguese')
    if not sentences:
        print("Nenhuma frase detectada na pergunta para busca de múltiplos contextos.")
        return []

    # Dictionary to store the best result for each unique document:
    # {document_index: (document_index, text, distance)}
    # This ensures uniqueness and that the lowest distance (best relevance) is maintained.
    consolidated_contexts_map = {}

    try:
        for sentence in sentences:
            print(f"Processando frase para múltiplos contextos: '{sentence}'")
            if not sentence.strip(): # Skip empty sentences that might be produced by sent_tokenize
                continue
            query_embedding = np.array(embedder_model.encode([sentence]), dtype=np.float32)
            distances, indices = faiss_index.search(query_embedding, k_per_sentence)

            for j in range(len(indices[0])):
                document_index = indices[0][j]
                distance_score = distances[0][j]

                if 0 <= document_index < len(context_documents):
                    # If the document has already been found, update if the new distance is smaller (more relevant)
                    if document_index not in consolidated_contexts_map or distance_score < consolidated_contexts_map[document_index][2]:
                        consolidated_contexts_map[document_index] = (document_index, context_documents[document_index], distance_score)

        # Convert the dictionary of consolidated contexts back to a list
        results_list = list(consolidated_contexts_map.values())
        # Sort the final results by distance (from most relevant to least)
        results_list.sort(key=lambda x: x[2])

        return results_list

    except Exception as e:
        print(f"Erro ao buscar múltiplos contextos: {e}")
        return []

# --- Funções de Teste ---
def test_context_search_interactive():
    """
    Interactive test function to demonstrate context search capabilities.

    Allows the user to input questions and choose between 'Full Context Search'
    or 'Multiple Contexts Search' strategies, displaying the most relevant
    contexts found.
    """
    try:
        context_documents, faiss_index, text_embedder = initialize_rag_system()
    except Exception as e:
        print(f"Erro fatal ao inicializar RAG: {e}")
        return

    while True:
        user_question = input("\nDigite uma pergunta (ou 'sair' para encerrar): ")
        if user_question.lower() == 'sair':
            break

        print("\nEscolha o tipo de busca:")
        print("1. Buscar Contexto Completo (pergunta inteira)")
        print("2. Buscar Múltiplos Contextos (segmentando a pergunta em frases)")
        search_choice = input("Opção (1 ou 2): ")

        retrieved_contexts = []
        if search_choice == '1':
            print(f"\nRealizando busca de contexto completo para: '{user_question}'")
            retrieved_contexts = search_with_full_query(user_question, context_documents, faiss_index, text_embedder, k_results=5)
        elif search_choice == '2':
            print(f"\nRealizando busca de múltiplos contextos para: '{user_question}'")
            retrieved_contexts = search_with_multiple_sentences(user_question, context_documents, faiss_index, text_embedder, k_per_sentence=3)
        else:
            print("Opção inválida. Tente novamente.")
            continue

        if not retrieved_contexts:
            print("Nenhum contexto encontrado.")
            continue

        print("\nContextos mais relevantes:")
        for doc_idx, text_content, distance_score in retrieved_contexts:
            print(f"\nÍndice Original do Documento: {doc_idx}, Distância: {distance_score:.4f}")
            print(f"Texto: {text_content[:500]}...") # Limita o texto para melhor visualização
            print("-" * 50)

if __name__ == "__main__":
    test_context_search_interactive()