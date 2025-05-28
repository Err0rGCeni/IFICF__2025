import time
from typing import Any, Generator
import gradio as gr
from utils.rag_retriever import inicializar_rag
from utils.llm_response import res_generate_API # A função unificada agora trata as estratégias de RAG e LLM
from utils.phrase_extractor import processar_arquivo
from utils.report_creation import generate_report

# --- Configurações Iniciais do RAG ---
rag_docs, rag_index, rag_embedder = [None, None, None]  # TODO: Test Only
# rag_docs, rag_index, rag_embedder = inicializar_rag()

# --- Constantes de Interface ---
STRINGS = {
    "APP_TITLE": "Sistema RAG para Análise de Documentos",
    "APP_DESCRIPTION": "Processe frases individualmente ou envie um arquivo para análise em lote usando um sistema RAG.",
    "TAB_0_TITLE": "Entrada de Frases via Arquivos",
    "TAB_0_SUBTITLE": "## 📝 Passo 1: Forneça as Frases",
    "TAB_1_TITLE": "Resultados da Análise",
    "TAB_1_SUBTITLE": "## 🤖 Passo 2: Visualize os Resultados",
    "TAB_2_TITLE": "Relatório e Exportação",
    "TAB_2_SUBTITLE": "## 📊 Passo 3: Exportar Resultados",
    "FILE_INPUT_LABEL": "Carregar Arquivo (.txt, .pdf, .docx) (DESABILITADO)",
    "FILE_INPUT_PLACEHOLDER": "Envie um arquivo de texto, PDF ou DOCX para extrair frases automaticamente.",
    "TEXT_INPUT_LABEL": "Frases para Análise",
    "TEXT_INPUT_PLACER_EMPTY": "PLACER_EMPTY",
    "TEXT_INPUT_PLACEHOLDER_EMPTY": "Digite as frases aqui (uma por linha) ou envie um arquivo para preencher.",
    "TEXT_INPUT_PLACEHOLDER_LOADED": "Frases do arquivo carregadas. Edite se necessário.",
    "TXTBOX_STATUS_IDLE": "Gerando Resposta, aguarde...",
    "TXTBOX_STATUS_OK": "Resposta gerada com sucesso!",
    "TXTBOX_STATUS_ERROR": "Erro ao gerar resposta. Verifique os detalhes.",
    "OUTPUT_RESULTS_LABEL": "Respostas Geradas",
    "OUTPUT_RESULTS_PLACEHOLDER_EMPTY": "Os resultados da análise aparecerão aqui.",
    "BTN_GENERATE_LABEL_DISABLED": "Aguardando Texto",
    "BTN_GENERATE_LABEL_ENABLED": "Gerar Análise",
    "BTN_CREATE_REPORT_DISABLED": "Aguardando Resposta da LLM",
    "BTN_GENERATE_REPORTL_ENABLED": "Gerar Relatório",
    "NO_PHRASES_PROVIDED_MSG": "Nenhuma frase foi fornecida para processamento.",
    "NO_VALID_PHRASES_MSG": "Nenhuma frase válida encontrada após a limpeza.",
    "PROCESSING_MESSAGE": "Processando... Por favor, aguarde.",
    "ERROR_MESSAGE": "Ocorreu um erro durante o processamento. Verifique os detalhes e tente novamente."
}
# --- Funções de Estados ---
def input_textbox_listener(input_text: str) -> gr.Button:
    """
    Listener para o campo de texto de entrada. Atualiza o botão de geração
    com base no conteúdo do campo de texto.
    """
    if len(input_text.strip()) > 2:
        return gr.Button(value=STRINGS["BTN_GENERATE_LABEL_ENABLED"], interactive=True)
    else:
        return gr.Button(value=STRINGS["BTN_GENERATE_LABEL_DISABLED"], interactive=False)

def status_textbox_listener(input_text: str) -> gr.Button:
    """
    Listener para o campo de texto de status. Atualiza o texto de status
    com base no conteúdo do campo de texto.
    """
    if input_text == STRINGS["TXTBOX_STATUS_OK"]:
        return gr.Button(value=STRINGS["BTN_GENERATE_REPORTL_ENABLED"], interactive=True)        
    else:
        return gr.Button(value=STRINGS["BTN_CREATE_REPORT_DISABLED"], interactive=False)

# --- Funções de Processamento ---
def extract_phrases_from_gradio_file(gradio_file: gr.File) -> gr.Textbox:
    """
    Utilizes the 'process_file' function from 'utils.phrase_extractor' to read the
    file content and extract phrases, returning them as a text block for Gradio.
    """
    if gradio_file is None:
        return gr.Textbox(value="", placeholder=STRINGS["TEXT_INPUT_PLACEHOLDER_EMPTY"])

    try:
        # Chama a função unificada de processamento de arquivo que retorna uma lista de frases
        phrases = processar_arquivo(gradio_file.name)
        
        phrases_text = "\n".join(phrases)
        return gr.Textbox(value=phrases_text, placeholder=STRINGS["TEXT_INPUT_PLACEHOLDER_LOADED"])
    except Exception as e:
        return gr.Textbox(value=f"Error: {e}", placeholder=STRINGS["TEXT_INPUT_PLACER_EMPTY"])

def process_phrases_with_rag_llm(input_phrases_text: str) -> Generator[tuple[gr.Textbox, gr.Textbox, gr.Tabs, gr.TabItem]]:
    """
    Receives a block of text (phrases separated by newlines) and processes it
    with the RAG+LLM API (`res_generate_API`) using a multiple-context strategy.
    Returns a status textbox, a formatted responses textbox, and updates tabs to switch to the results tab.
    """
    print(f"Processando o bloco de frases para geração de resposta: \"{input_phrases_text[:100]}...\"")
    current_symbol = "♾️"  # Emojis para indicar status de processamento e sucesso    

    # --- Ação 1: Mudar de aba IMEDIATAMENTE e mostrar mensagem de processamento ---
    # O 'yield' envia: (Status, Resultado, Tabs)
    yield gr.Textbox(value=STRINGS["TXTBOX_STATUS_IDLE"], interactive=False), \
          gr.Textbox(value="", interactive=False), \
          gr.Tabs(selected=1), \
          gr.TabItem(STRINGS["TAB_1_TITLE"]+" "+current_symbol, interactive=True)
    
    time.sleep(1)  # Simula um pequeno atraso para processamento

    try:
        # Chama a função unificada de geração de resposta, especificando a estratégia RAG
        # O LLM então usará os múltiplos contextos recuperados para gerar uma única resposta consolidada.

#        llm_response = res_generate_API(
#            frase_entrada=input_phrases_text,
#            documentos=rag_docs,
#            index=rag_index,
#            embedder=rag_embedder,
#            llm_choice='gemini', # ou 'ollama', conforme a necessidade
#            rag_strategy='multiplo' # A chave para usar a busca por múltiplos contextos
#        )

        with open("./sandbox/respostateste.txt", "r", encoding="utf-8") as arquivo:
            llm_response = arquivo.read() #TODO: Test Only

        status_message = STRINGS["TXTBOX_STATUS_OK"]
        formatted_output = f"--- Resposta Fornecida pela LLM ---\n{llm_response}\n"
        current_symbol = "✅" 

    except Exception as e:
        status_message = STRINGS["TXTBOX_STATUS_ERROR"]
        formatted_output = f"\n{STRINGS['ERROR_MESSAGE']}\nDetalhes: {e}"
        current_symbol = "⚠️"

    # --- Ação 3: Retornar o resultado final e o status ---
    # A aba já está selecionada, então gr.Tabs() aqui apenas satisfaz a assinatura e mantém a aba atual.
    yield gr.Textbox(value=status_message, interactive=False), \
          gr.Textbox(value=formatted_output, interactive=False), \
          gr.Tabs(), \
          gr.TabItem(STRINGS["TAB_1_TITLE"]+" "+current_symbol, interactive=True)

def create_report(llm_response: str) -> tuple[gr.Plot, gr.Plot, gr.Tabs, gr.TabItem]:   
    """
    Placeholder para a função de geração de relatório.
    Aqui você pode implementar a lógica para gerar um relatório baseado na resposta da LLM.
    Por enquanto, apenas retorna a aba atual sem alterações.
    """
    # Implementar lógica de geração de relatório aqui
    print("Gerando relatório...")
    df_group, df_group_describe, df_individuals, df_individuals_describe, plot_pie, plot_bar, plot_tree, report_path = generate_report(llm_response)  # Placeholder para a função de geração de relatório
    
    return gr.DataFrame(df_group), \
            gr.DataFrame(df_group_describe), \
            gr.DataFrame(df_individuals), \
            gr.DataFrame(df_individuals_describe), \
            gr.Plot(plot_pie), \
            gr.Plot(plot_bar), \
            gr.Plot(plot_tree), \
            gr.DownloadButton(value=report_path, label="📥 Baixar Relatório", interactive=True), \
            gr.Tabs(selected=2), \
            gr.TabItem(STRINGS["TAB_2_TITLE"]+" ✅", interactive=True)
# --- Construção da Interface Gradio ---
with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    current_tab_index = gr.State(0)
    gr.Markdown(f"# {STRINGS["APP_TITLE"]}")
    gr.Markdown(STRINGS["APP_DESCRIPTION"])

    with gr.Tabs() as tabs_component:
        with gr.TabItem(STRINGS["TAB_0_TITLE"], id=0):
            gr.Markdown(STRINGS["TAB_0_SUBTITLE"])
            
            in_file_user = gr.File(
                label=STRINGS["FILE_INPUT_LABEL"],
                type="filepath",
                file_types=['.txt', '.pdf', '.docx'],
                interactive=False
            )
            
            in_txt_phrases = gr.Textbox(
                label=STRINGS["TEXT_INPUT_LABEL"],
                placeholder=STRINGS["TEXT_INPUT_PLACEHOLDER_EMPTY"],
                lines=10,
                interactive=True
            )

            btn_process = gr.Button(STRINGS["BTN_GENERATE_LABEL_DISABLED"], interactive=False)

            in_file_user.upload(
                fn=extract_phrases_from_gradio_file,
                inputs=in_file_user,
                outputs=in_txt_phrases
            )

            in_txt_phrases.change(
                fn=input_textbox_listener,
                inputs=in_txt_phrases,
                outputs=btn_process
            )            

        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_1:
            gr.Markdown(STRINGS["TAB_1_SUBTITLE"])

            out_txt_status = gr.Textbox(
                label="Status do Processamento:",
                interactive=False,
                value=""
            )

            out_txt_response = gr.Textbox(
                label=STRINGS["OUTPUT_RESULTS_LABEL"],
                lines=15,
                interactive=False,
                placeholder=STRINGS["OUTPUT_RESULTS_PLACEHOLDER_EMPTY"]
            )

            btn_return_inputs = gr.Button("🔙 Voltar para Entrada de Frases")
            
            btn_create_report = gr.Button("📊 Gerar Relatório", interactive=False)

            out_txt_status.change(
                fn=status_textbox_listener,
                inputs=out_txt_status,
                outputs=btn_create_report
            )

        with gr.TabItem(STRINGS["TAB_2_TITLE"] + " 🔒", interactive=False, id=2) as tab_2:
            gr.Markdown(STRINGS["TAB_2_SUBTITLE"])

            with gr.Row():
                grouped_data = gr.DataFrame(label="Tabela de Resultados Agrupados")
                grouped_describe = gr.DataFrame(label="Descrição Estatística dos Resultados Agrupados")

            with gr.Row():
                individual_data = gr.DataFrame(label="Tabela de Resultados Individuais")
                individual_describe = gr.DataFrame(label="Descrição Estatística dos Resultados Individuais")
            
            out_graph_pie = gr.Plot(label="Gráfico de Setores da Classificação")

            out_graph_hist = gr.Plot(label="Gráfico de Barras de Classificação")

            out_graph_tree = gr.Plot(label="Gráfico Treemap de Classificação")

            btn_download_report = gr.DownloadButton(label="📥 Baixar Relatório", interactive=True)

            btn_return_inputs

    btn_process.click(
        fn=process_phrases_with_rag_llm,
        inputs=in_txt_phrases,
        outputs=[out_txt_status, out_txt_response, tabs_component, tab_1]
    )

    btn_create_report.click(
        fn=create_report,  # Placeholder para geração de relatório
        inputs=out_txt_response,
        outputs=[grouped_data, grouped_describe, individual_data, individual_describe, out_graph_pie, out_graph_hist, out_graph_tree, btn_download_report, tabs_component, tab_2]
    )

    btn_return_inputs.click(
    fn=lambda: gr.Tabs(selected=0),  # Volta para a aba de entrada
    inputs=[],
    outputs=tabs_component
    )

if __name__ == "__main__":
    interface.launch()