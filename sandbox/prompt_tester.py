import ollama
import gradio as gr
from utils.rag_retriever import inicializar_rag, buscar_contexto  # Importe as funções do módulo

print("Inicializando...")

# Função para gerar resposta com o Ollama (agora usa prompt customizável)
def gerar_resposta_custom(frase_entrada, prompt_custom, documentos, index, embedder):
    """Gera uma resposta baseada no contexto recuperado e um prompt customizável."""
    contextos_com_distancia = buscar_contexto(frase_entrada, documentos, index, embedder)
    # Extrai apenas o texto dos documentos da lista de tuplas
    contexto = [texto for _, texto, _ in contextos_com_distancia]
    contexto_str = "\n".join(contexto)

    # Insere o contexto e a frase de entrada no prompt customizável
    prompt = prompt_custom.replace("{{context}}", contexto_str).replace("{{frase_entrada}}", frase_entrada)

    # Imprime o prompt no terminal
    print("\n--- Prompt Gerado ---")
    print(prompt)
    print("--- Fim do Prompt ---")

    resposta = ollama.generate(model='gemma3:1b', prompt=prompt)
    return contexto_str, resposta['response']

# Função principal para a interface Gradio (agora com prompt customizável e múltiplas saídas)
def interface_rag_alternativa(frase_entrada, prompt_custom):
    """Função chamada pela interface Gradio alternativa."""
    contexto, resposta = gerar_resposta_custom(frase_entrada, prompt_custom, documentos, index, embedder)
    return contexto, resposta

# Inicialização do RAG (mantida)
print("Inicializando RAG...")
documentos, index, embedder = inicializar_rag()

# Prompt padrão (pode ser editado pelo usuário)
prompt_padrao = """
Com base no seguinte contexto:
{{context}}

Responda à seguinte pergunta:
{{frase_entrada}}
"""

# Configuração da interface Gradio alternativa
with gr.Blocks() as interface_alternativa:
    with gr.Column(scale=1):
        frase_entrada_input = gr.Textbox(label="Frase de Entrada", placeholder="Ex.: O que é função puberal?")
        prompt_input = gr.Textbox(label="Prompt Customizado", value=prompt_padrao, lines=10)
        botao_enviar = gr.Button("Enviar")
    with gr.Column(scale=1):
        contexto_output = gr.Textbox(label="Contexto Recuperado")
        resposta_output = gr.Textbox(label="Resposta da LLM")

    botao_enviar.click(
        fn=interface_rag_alternativa,
        inputs=[frase_entrada_input, prompt_input],
        outputs=[contexto_output, resposta_output]
    )

# Iniciar a interface alternativa
print("Gerando Interface Alternativa...")
interface_alternativa.launch(share=True)
