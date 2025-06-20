import faiss
import gradio as gr
from typing import Any, Generator
from sentence_transformers import SentenceTransformer
from utils.rag_llm_response import generate_response_with_llm # A função unificada agora trata as estratégias de RAG e LLM
from utils.phrase_extractor import process_file_content
#from utils.report_creation import generate_report
from utils.api_gemini import api_generate
from .strings import STRINGS
# DEPRECATED: A função volta com a consolidação de um futuro OCR.
#def extract_phrases_from_gradio_file(gradio_file: gr.File) -> gr.Textbox:
#    """
#    Utilizes the 'process_file' function from 'utils.phrase_extractor' to read the
#    file content and extract phrases, returning them as a text block for Gradio.
#    """
#    if gradio_file is None:
#        return gr.Textbox(value="", placeholder=STRINGS["TEXT_INPUT_PLACEHOLDER_EMPTY"])
#
#    try:
#        # Chama a função unificada de processamento de arquivo que retorna uma lista de frases
#        phrases = process_file_content(gradio_file.name)
#        
#        phrases_text = "\n".join(phrases)
#        return gr.Textbox(value=phrases_text, placeholder=STRINGS["TEXT_INPUT_PLACEHOLDER_LOADED"])
#    except Exception as e:
#        return gr.Textbox(value=f"Error: {e}", placeholder=STRINGS["TEXT_INPUT_PLACER_EMPTY"])

# DEPRECATED: A função volta com a consolidação de um futuro RAG.
def process_phrases_with_rag_llm(input_phrases_text: str, rag_docs:list[str], rag_index:faiss.Index, rag_embedder:SentenceTransformer) -> Generator[tuple[gr.Textbox, gr.Textbox, gr.Tabs, gr.TabItem]]:
    """
    Receives a block of text (phrases separated by newlines) and processes it
    with the RAG+LLM API (`res_generate_API`) using a multiple-context strategy.
    Returns a status textbox, a formatted responses textbox, and updates tabs to switch to the results tab.
    """
    print(f"Processando o bloco de frases para geração de resposta: \"{input_phrases_text[:100]}...\"")
    current_symbol = " ♾️"  # Emojis para indicar status de processamento e sucesso    

    # --- Ação 1: Mudar de aba IMEDIATAMENTE e mostrar mensagem de processamento ---
    # O 'yield' envia: (Status, Resultado, Tabs)
    yield (
        gr.update(value=STRINGS["TXTBOX_STATUS_IDLE"], interactive=False),
        gr.update(value="", interactive=False),
        gr.update(selected=1),
        gr.update(label=STRINGS["TAB_1_TITLE"]+current_symbol, interactive=True)
        )
    
    # time.sleep(1)  # Simula um pequeno atraso para processamento

    try:
        # Chama a função unificada de geração de resposta, especificando a estratégia RAG
        # O LLM então usará os múltiplos contextos recuperados para gerar uma única resposta consolidada.

        llm_response = generate_response_with_llm(
            input_phrase=input_phrases_text,
            documents=rag_docs,
            index=rag_index,
            embedder=rag_embedder,
            llm_choice='gemini', # ou 'ollama', conforme a necessidade
            rag_strategy='multiple' # A chave para usar a busca por múltiplos contextos
        )

#        with open("./sandbox/respostateste.txt", "r", encoding="utf-8") as arquivo:
#            llm_response = arquivo.read() #TODO: Test Only

        status_message = STRINGS["TXTBOX_STATUS_OK"]
        formatted_output = f"--- Resposta Fornecida pela LLM ---\n{llm_response}\n"
        current_symbol = " ✅" 

    except Exception as e:
        status_message = STRINGS["TXTBOX_STATUS_ERROR"]
        formatted_output = f"\n{STRINGS['--- Erro ---']}\nDetalhes: {e}"
        current_symbol = " ⚠️"

    # --- Ação 3: Retornar o resultado final e o status ---
    # A aba já está selecionada, então gr.Tabs() aqui apenas satisfaz a assinatura e mantém a aba atual.
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value=formatted_output, interactive=False),
        gr.update(),
        gr.update(label=STRINGS["TAB_1_TITLE"]+current_symbol, interactive=True)
    )

def process_phrases_with_api_llm(input_phrases_text: str) -> Generator[tuple[gr.Textbox, gr.Textbox, gr.Tabs, gr.TabItem]]:
    """
    Receives a block of text and processes it
    with the API (`res_generate_API`).
    Returns a status textbox, a formatted responses textbox, and updates tabs to switch to the results tab.
    """
    print(f"Processando o bloco de frases para geração de resposta: \"{input_phrases_text[:100]}...\"")
    current_symbol = " ♾️"  # Emojis para indicar status de processamento e sucesso    

    # --- Ação 1: Mudar de aba IMEDIATAMENTE e mostrar mensagem de processamento ---
    # O 'yield' envia: (Status, Resultado, Tabs)
    yield (
        gr.update(value=STRINGS["TXTBOX_STATUS_IDLE"], interactive=False),
        gr.update(value="", interactive=False),
        gr.update(selected=1),
        gr.update(label=STRINGS["TAB_1_TITLE"]+current_symbol, interactive=True)
        )
    
    # time.sleep(1)  # Simula um pequeno atraso para processamento

    try:
        # Chama a função unificada de geração de resposta, especificando a estratégia RAG
        # O LLM então usará os múltiplos contextos recuperados para gerar uma única resposta consolidada.

#        llm_response = generate_response_with_llm(
#            input_phrase=input_phrases_text,
#            documents=rag_docs,
#            index=rag_index,
#            embedder=rag_embedder,
#            llm_choice='gemini', # ou 'ollama', conforme a necessidade
#            rag_strategy='multiple' # A chave para usar a busca por múltiplos contextos
#        )

#        with open("./sandbox/respostateste.txt", "r", encoding="utf-8") as arquivo:
#            llm_response = arquivo.read() #TEST: Test Only

        llm_response = api_generate(user_input=input_phrases_text)

        status_message = STRINGS["TXTBOX_STATUS_OK"]
        formatted_output = f"--- Resposta Fornecida pela LLM ---\n{llm_response}\n"
        current_symbol = " ✅" 

    except Exception as e:
        status_message = STRINGS["TXTBOX_STATUS_ERROR"]
        formatted_output = f"\n{STRINGS['--- Erro ---']}\nDetalhes: {e}"
        current_symbol = " ⚠️"

    # --- Ação 3: Retornar o resultado final e o status ---
    # A aba já está selecionada, então gr.Tabs() aqui apenas satisfaz a assinatura e mantém a aba atual.
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value=formatted_output, interactive=False),
        gr.update(),
        gr.update(label=STRINGS["TAB_1_TITLE"]+current_symbol, interactive=True)
    )