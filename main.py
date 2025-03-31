import ollama
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import gradio as gr

# Função para carregar e processar o conhecimento
def inicializar_rag(caminho_arquivo):
    """Inicializa o modelo de embeddings, documentos e índice FAISS."""
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        documentos = f.read().split('\n\n')  # Divide em parágrafos
    embeddings = embedder.encode(documentos, convert_to_tensor=False)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return embedder, documentos, index

# Função para buscar contexto relevante
def buscar_contexto(pergunta, embedder, documentos, index, k=3):
    """Busca os k documentos mais relevantes para a pergunta."""
    query_embedding = embedder.encode([pergunta], convert_to_tensor=False)
    D, I = index.search(query_embedding, k)
    return [documentos[i] for i in I[0]]

# Função para gerar resposta com o Ollama
def gerar_resposta(pergunta, embedder, documentos, index):
    """Gera uma resposta baseada no contexto recuperado."""
    contexto = buscar_contexto(pergunta, embedder, documentos, index)
    contexto_str = "\n".join(contexto)
    prompt = f"Com base no seguinte contexto:\n{contexto_str}\n\nRetorne conceito significativo e código CIF relacionado às frases: {pergunta}"
    resposta = ollama.generate(model='llama3.2', prompt=prompt)
    return resposta['response']

# Função principal para a interface Gradio
def interface_rag(pergunta):
    """Função chamada pela interface Gradio."""
    resposta = gerar_resposta(pergunta, embedder, documentos, index)
    return resposta

# Inicialização do RAG
caminho_arquivo = 'RAG_exemplos.txt'
embedder, documentos, index = inicializar_rag(caminho_arquivo)

# Configuração da interface Gradio
interface = gr.Interface(
    fn=interface_rag,
    inputs=[
        gr.File(label="Faça upload do arquivo (.txt, .doc, .docx, .pdf)"),
        gr.Textbox(label="Digite sua pergunta", placeholder="Ex.: O que é isso?")
    ],
    outputs=gr.Textbox(label="Resposta"),
    title="Sistema RAG",
    description="Faça upload de um arquivo e pergunte algo sobre seu conteúdo."
)

# Iniciar a interface
interface.launch()
