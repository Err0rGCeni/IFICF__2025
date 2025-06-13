import os
import pandas as pd # Importado para type hinting em _update_dataframes_from_states
import plotly.graph_objects as go # Importado para type hinting em _update_plots_from_states
import gradio as gr
from typing import Any, Generator, Tuple, Optional
from functools import partial

from utils.rag_retriever import initialize_rag_system
from utils.report_creation import process_report_data, create_report_plots, generate_report_pdf

#from .scripts import extract_phrases_from_gradio_file, process_phrases_with_rag_llm
from .scripts import process_phrases_with_rag_llm
from .strings import STRINGS

# --- Configurações Iniciais do RAG ---
#rag_docs, rag_index, rag_embedder = [None, None, None] # TODO: Apenas para Teste
rag_docs, rag_index, rag_embedder = initialize_rag_system()
img1 = os.path.join(os.getcwd(), "static", "images", "logo.jpg")

# --- Função Auxiliadora para Processamento de Frases ---
process_fn_with_rag_args = partial(
    process_phrases_with_rag_llm,
    # Passe os argumentos fixos aqui.
    rag_docs=rag_docs,
    rag_index=rag_index,
    rag_embedder=rag_embedder
)

# --- Funções Auxiliares (Listeners e Controladores de UI) ---
def _handle_input_text_change(text_input: str) -> gr.Button:
    """
    Listener for the input textbox. Updates the generation button
    based on the content of the textbox.
    """
    if len(text_input.strip()) > 2:
        return gr.update(value=STRINGS["BTN_PROCESS_INPUT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(value=STRINGS["BTN_PROCESS_INPUT_LABEL_DISABLED"], interactive=False, variant="secondary")

def _handle_status_text_change(status_text: str) -> gr.Button:
    """
    Listener for the status textbox. Updates the report creation button
    based on the content of the status textbox.
    """
    if status_text == STRINGS["TXTBOX_STATUS_OK"]:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")

def _switch_to_report_tab_and_enable_interaction() -> Tuple[gr.Tabs, gr.TabItem]:
    """
    Switches to the report tab and enables interaction for it.
    Returns updated Tabs and TabItem components.
    """
    return gr.update(selected=2), gr.update(label=STRINGS["TAB_2_TITLE"] + " ✅", interactive=True)

# --- Atualizar Componentes Visíveis a partir de States ---
def _update_dataframe_components(group_data_df: Optional[pd.DataFrame],
                                 group_description_df: Optional[pd.DataFrame],
                                 individuals_data_df: Optional[pd.DataFrame],
                                 individuals_description_df: Optional[pd.DataFrame]
                                 ) -> Tuple[gr.DataFrame, gr.DataFrame, gr.DataFrame, gr.DataFrame]:
    """
    Updates the visible Gradio DataFrame components with new data.
    """
    return (
        gr.DataFrame(value=group_data_df),
        gr.DataFrame(value=group_description_df),
        gr.DataFrame(value=individuals_data_df),
        gr.DataFrame(value=individuals_description_df)
    )

def _update_plot_components(pie_chart_figure: Optional[go.Figure],
                            bar_chart_figure: Optional[go.Figure],
                            tree_map_figure: Optional[go.Figure]
                            ) -> Tuple[gr.Plot, gr.Plot, gr.Plot]:
    """
    Updates the visible Gradio Plot components with new figures.
    """
    print("Atualizando gráficos visíveis...")
    return (
        gr.Plot(value=pie_chart_figure),
        gr.Plot(value=bar_chart_figure),
        gr.Plot(value=tree_map_figure)
    )

def _update_download_button_component(report_file_path: Optional[str]) -> gr.DownloadButton:
    """
    Updates the Gradio DownloadButton component with the PDF path.
    """
    if report_file_path:
        return gr.update(value=report_file_path, label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ERROR"], interactive=False, variant="secondary")


# --- Construção da Interface Gradio ---
with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    # --- States para Armazenar Dados Brutos (entre as etapas do .then()) ---
    state_dataframe_group = gr.State(None)
    state_dataframe_group_description = gr.State(None)
    state_dataframe_individuals = gr.State(None)
    state_dataframe_individuals_description = gr.State(None)
    state_figure_pie_chart = gr.State(None)
    state_figure_bar_chart = gr.State(None)
    state_figure_tree_map = gr.State(None)
    state_report_file_path = gr.State(None)
    state_llm_response = gr.State(None)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(
                f"# {STRINGS['APP_TITLE']}",
                elem_id="md_app_title",
            )
            gr.Markdown(
                f"{STRINGS['APP_DESCRIPTION']}",
                elem_id="md_app_description",
            )
    
        gr.Image(
        value=img1,
        height=64,
        elem_id="logo_img",
        placeholder="CIF Link Logo",
        container=False,
        show_label=False,
        show_download_button=False,
        scale=0
        )

    with gr.Tabs() as tabs_main_navigation:
        with gr.TabItem(STRINGS["TAB_0_TITLE"], id=0):
            gr.Markdown(STRINGS["TAB_0_SUBTITLE"])
# DEPRECATED: gr.File volta em uma futura versão 
#            file_input_user_document = gr.File(
#                label=STRINGS["FILE_INPUT_LABEL"],
#                type="filepath",
#                file_types=['.txt', '.pdf', '.docx'],
#                interactive=False
#            )

            textbox_input_phrases = gr.Textbox(
                label=STRINGS["TXTBOX_INPUT_PHRASES_LABEL"],
                placeholder=STRINGS["TXTBOX_INPUT_PHRASES_PLACEHOLDER"],
                lines=10,
                interactive=True
            )

            button_process_input = gr.Button(STRINGS["BTN_PROCESS_INPUT_LABEL_DISABLED"], interactive=False, variant="secondary")

#            file_input_user_document.upload(
#                fn=extract_phrases_from_gradio_file,
#                inputs=file_input_user_document,
#                outputs=textbox_input_phrases
#            )

            textbox_input_phrases.change(
                fn=_handle_input_text_change,
                inputs=textbox_input_phrases,
                outputs=button_process_input
            )

        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_item_processing_results:
            gr.Markdown(STRINGS["TAB_1_SUBTITLE"])

            textbox_output_status = gr.Textbox(
                label=STRINGS["TXTBOX_STATUS_LABEL"],
                interactive=False,
                value=""
            )

            textbox_output_llm_response = gr.Textbox(
                label=STRINGS["TXTBOX_OUTPUT_LLM_RESPONSE_LABEL"],
                lines=15,
                interactive=False,
                placeholder=STRINGS["TXTBOX_OUTPUT_LLM_RESPONSE_PLACEHOLDER"]
            )

            button_create_report = gr.Button(STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")
            button_return_to_input_tab_from_results = gr.Button(STRINGS["BTN_RETURN_LABEL"], variant="secondary")

            textbox_output_status.change(
                fn=_handle_status_text_change,
                inputs=textbox_output_status,
                outputs=button_create_report
            )

            # Captura a resposta da LLM no estado para uso posterior em outras funções
            textbox_output_llm_response.change(
                fn=lambda response_text: response_text, # Função identidade para passar o valor
                inputs=textbox_output_llm_response,
                outputs=state_llm_response
            )

        with gr.TabItem(STRINGS["TAB_2_TITLE"] + " 🔒", interactive=False, id=2) as tab_item_report_visualization:
            gr.Markdown(STRINGS["TAB_2_SUBTITLE"])

            with gr.Row():
                dataframe_display_grouped_data = gr.DataFrame(label=STRINGS["DF_GROUP_DATA"])
                dataframe_display_grouped_description = gr.DataFrame(label=STRINGS["DF_GROUP_DESC"])

            with gr.Row():
                dataframe_display_individual_data = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DATA"])
                dataframe_display_individual_description = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DESC"])

            plot_display_pie_chart = gr.Plot(label=STRINGS["PLOT_PIE_LABEL"])
            plot_display_bar_chart = gr.Plot(label=STRINGS["PLOT_BAR_LABEL"])
            plot_display_tree_map = gr.Plot(label=STRINGS["PLOT_TREE_LABEL"])

            download_button_report_pdf = gr.DownloadButton(label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")
            button_return_to_input_tab_from_report = gr.Button(STRINGS["BTN_RETURN_LABEL"], variant="secondary") # Botão para voltar à aba 0 da aba 2

    # --- FLUXO DE EVENTOS MULTI-CHAINING PARA O RELATÓRIO ---
    button_process_input.click(
        fn=process_fn_with_rag_args,
        inputs=[textbox_input_phrases],
        outputs=[textbox_output_status, textbox_output_llm_response, tabs_main_navigation, tab_item_processing_results]
    )

    button_create_report.click(
        fn=_switch_to_report_tab_and_enable_interaction, # 1. Muda de aba e a habilita - Switches tab and enables it
        inputs=[],
        outputs=[tabs_main_navigation, tab_item_report_visualization]
    ).then(
        fn=process_report_data, # 2. Processa a resposta da LLM e salva os DataFrames brutos nos states
        inputs=[state_llm_response],
        outputs=[
            state_dataframe_group, state_dataframe_group_description,
            state_dataframe_individuals, state_dataframe_individuals_description
        ]
    ).then(
        fn=_update_dataframe_components, # 3. Atualiza os componentes Gradio DataFrame visíveis
        inputs=[state_dataframe_group, state_dataframe_group_description, state_dataframe_individuals, state_dataframe_individuals_description],
        outputs=[dataframe_display_grouped_data, dataframe_display_grouped_description, dataframe_display_individual_data, dataframe_display_individual_description]
    ).then(
        fn=create_report_plots, # 4. Pega DataFrames dos states e gera os gráficos Plotly brutos nos states
        inputs=[state_dataframe_group, state_dataframe_individuals],
        outputs=[state_figure_pie_chart, state_figure_bar_chart, state_figure_tree_map]
    ).then(
        fn=_update_plot_components, # 5. Atualiza os componentes Gradio Plot visíveis
        inputs=[state_figure_pie_chart, state_figure_bar_chart, state_figure_tree_map],
        outputs=[plot_display_pie_chart, plot_display_bar_chart, plot_display_tree_map]
    ).then(
        fn=generate_report_pdf, # 6. Gera o PDF a partir de todos os dados e gráficos (states)
        inputs=[
            state_llm_response, # Resposta LLM original - Original LLM response
            state_dataframe_group, state_dataframe_group_description, state_dataframe_individuals, state_dataframe_individuals_description,
            state_figure_pie_chart, state_figure_bar_chart, state_figure_tree_map
        ],
        outputs=[state_report_file_path] # Atualiza o state do caminho do PDF
    ).then(
        fn=_update_download_button_component, # 7. Atualiza o botão de download
        inputs=[state_report_file_path],
        outputs=[download_button_report_pdf]
    )

    # --- Eventos para voltar para a aba de entrada ---
    button_return_to_input_tab_from_results.click(
        fn=lambda: gr.Tabs(selected=0),
        inputs=[],
        outputs=tabs_main_navigation
    )
    button_return_to_input_tab_from_report.click(
        fn=lambda: gr.Tabs(selected=0),
        inputs=[],
        outputs=tabs_main_navigation
    )

if __name__ == "__main__":
    print("Executando a aplicação Gradio...")
    interface.launch()