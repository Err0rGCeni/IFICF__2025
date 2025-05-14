import ollama
import gradio as gr
import numpy as np
from utils.faiss_rag import inicializar_rag, buscar_contexto  # Importe as funções do módulo

print("Inicializando...")

# Função para gerar resposta com o Ollama (agora recebe embedder)
def gerar_resposta(frase_entrada, documentos, index, embedder):
    """Gera uma resposta baseada no contexto recuperado."""
    contextos_com_distancia = buscar_contexto(frase_entrada, documentos, index, embedder)
    # Extrai apenas o texto dos documentos da lista de tuplas
    contexto = [texto for _, texto, _ in contextos_com_distancia]
    contexto_str = "\n".join(contexto)

    # Prompt com instruções detalhadas sobre CIF
    prompt = f"""
        Você é um assistente de saúde especializado na Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF).
        Sua tarefa é classificar **Frase** com os códigos CIF. Se o contexto for insuficiente, você pode usar seu conhecimento prévio.
        **RAG**:
        {contexto_str}

        **Frase**:
        {frase_entrada}

        **Formato da Resposta**:
        - **Conceito**: [Descrição do conceito significativo]
        - **Código CIF**: [Código CIF + nomeclatura]
        - **Justificativa**: [Explicação baseada no RAG]
    """

    print("\n--- Prompt Gerado ---")
    print(prompt)
    print("--- Fim do Prompt ---")
    resposta = ollama.generate(model='gemma3:1b', prompt=prompt)
    return resposta['response']

# Função principal para a interface Gradio (agora recebe embedder e passa para gerar_resposta)
def interface_rag(frase_entrada):
    """Função chamada pela interface Gradio."""
    resposta = gerar_resposta(frase_entrada, documentos, index, embedder)  # Passe o embedder aqui
    return resposta

# Inicialização do RAG (agora retorna documentos, index e embedder)
print("Inicializando RAG...")
documentos, index, embedder = inicializar_rag()

# Configuração da interface Gradio (mantida)
interface = gr.Interface(
    fn=interface_rag,
    inputs=gr.Textbox(label="Digite sua frase", placeholder="Ex.: O que é função puberal?"),
    outputs=gr.Textbox(label="Resposta"),
    title="Sistema RAG para CIF",
    description="Pergunte algo sobre Funções Corporais, Estruturas Corporais, Atividades e Participação ou Fatores Ambientais com base na CIF."
)

# Iniciar a interface (mantido)
print("Gerando Interface...")
interface.launch()