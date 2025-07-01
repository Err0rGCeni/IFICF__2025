# pages/main/scripts.py
import faiss
import gradio as gr
from typing import Any, Generator
#from sentence_transformers import SentenceTransformer
#from utils.rag_llm_response import generate_response_with_llm # A função unificada agora trata as estratégias de RAG e LLM
#from utils.phrase_extractor import process_file_content
#from utils.report_creation import generate_report
from utils.apis.gemini import api_generate
from .strings import STRINGS
# DEPRECATED: A função era um protótipo para criação de Contexto RAG.
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
'''
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
'''
def process_inputs_to_api(
    input_text: str,
    input_file: Any  # Objeto de arquivo do Gradio (ex: tempfile._TemporaryFileWrapper)
) -> Generator[tuple, None, None]:
    """
    Processa a entrada do usuário (texto ou arquivo) com a API do Gemini.

    Esta função serve como o handler para a interface Gradio. Ela implementa a
    lógica XOR para garantir que apenas uma forma de entrada seja fornecida,
    atualiza a UI com o status e exibe o resultado da análise.

    Args:
        input_text: O conteúdo do componente gr.Textbox.
        input_file: O objeto do componente gr.File. É None se nenhum arquivo for carregado.

    Yields:
        Atualizações para os componentes da interface do Gradio.
    """
    current_symbol = " ♾️"  # Símbolo de processamento
    formatted_output = ""
    status_message = STRINGS["TXTBOX_STATUS_IDLE"]

    # --- Ação 1: Atualiza a UI para mostrar que o processamento começou ---
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value="", interactive=False),
        gr.update(selected=1),  # Muda para a aba de resultados
        gr.update(label=STRINGS["TAB_1_TITLE"] + current_symbol, interactive=True)
    )

    try:
        # --- Ação 2: Lógica de validação XOR para as entradas da UI ---
        texto_fornecido = bool(input_text and input_text.strip())
        arquivo_fornecido = input_file is not None

        if texto_fornecido and arquivo_fornecido:
            raise ValueError("Por favor, forneça texto OU um arquivo PDF, não ambos.")
        
        if not texto_fornecido and not arquivo_fornecido:
            raise ValueError("Nenhuma entrada fornecida. Por favor, digite um texto ou faça o upload de um arquivo.")

        # --- Ação 3: Chama o backend com o parâmetro correto ---
        params_para_api = {}
        if texto_fornecido:
            print(f"Processando via texto: \"{input_text[:100]}...\"")
            params_para_api['input_text'] = input_text
        elif arquivo_fornecido:
            # O objeto do Gradio tem um atributo .name que contém o caminho temporário do arquivo
            print(f"Processando via arquivo: {input_file.name}")
            params_para_api['input_file'] = input_file.name

        # Chama a função de backend com os parâmetros corretos
        llm_response = api_generate(**params_para_api)

        status_message = STRINGS["TXTBOX_STATUS_OK"]
        formatted_output = f"--- Resposta Fornecida pela LLM ---\n{llm_response}\n"
        current_symbol = " ✅"

    except Exception as e:
        # Captura qualquer erro (de validação ou da API) e o exibe na UI
        status_message = STRINGS["TXTBOX_STATUS_ERROR"]
        formatted_output = f"\n--- Erro ao Processar ---\nDetalhes: {e}"
        current_symbol = " ⚠️"
        print(f"ERRO na interface Gradio: {e}") # Loga o erro completo no console

    # --- Ação Final: Retorna o resultado (sucesso ou erro) para a UI ---
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value=formatted_output, interactive=True), # Permite copiar o resultado
        gr.update(),
        gr.update(label=STRINGS["TAB_1_TITLE"] + current_symbol, interactive=True)
    )