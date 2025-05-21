import gradio as gr
from utils.rag_retriever import inicializar_rag, buscar_contexto

print("Inicializando FAISS...")
documentos, index, embedder = inicializar_rag()

# Função para formatar os resultados da busca
def formatar_resultados(contextos):
    if not contextos:
        return "Nenhum contexto encontrado."
    
    resultado = "**Contextos mais relevantes:**\n\n"
    for idx, texto, distancia in contextos:
        resultado += f"**Índice:** {idx} | **Distância:** {distancia:.4f}\n\n"
        resultado += f"**Texto:** {texto[:3200]}...\n\n"
    return resultado

# Função principal para a interface Gradio
def buscar_contexto_interface(pergunta: str, k: int):
    try:
        # Inicializar RAG (carrega índice ou cria novo)
        # documentos, index, embedder = inicializar_rag()
        
        # Buscar contextos
        contextos = buscar_contexto(pergunta, documentos, index, embedder, k)
        
        # Formatar e retornar resultados
        return formatar_resultados(contextos)
    except Exception as e:
        return f"Erro ao buscar contexto: {e}"

# Configurar a interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# RAG com FAISS - Busca de Contexto")
    gr.Markdown("Digite uma pergunta para buscar contextos relevantes nos documentos carregados.")
    
    with gr.Row():
        pergunta_input = gr.Textbox(label="Pergunta", placeholder="Digite sua pergunta aqui...")
        k_input = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Número de resultados (k)")
    
    buscar_button = gr.Button("Buscar")
    output = gr.Markdown(label="Resultados")
    
    # Conectar o botão à função de busca
    buscar_button.click(
        fn=buscar_contexto_interface,
        inputs=[pergunta_input, k_input],
        outputs=output
    )

# Iniciar a interface
if __name__ == "__main__":
    demo.launch()