# pages/main/view.py
import os
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Tuple, Optional, Dict

from utils.report.report_creation import generate_report_pdf
from utils.report.graph_creation import create_report_plots
from utils.report.dataframe_creation import process_report_data
from .scripts import process_inputs_to_api
from .strings import STRINGS

# --- Constantes ---
LOGO = os.path.join(os.getcwd(), "static", "images", "logo.jpg")
RADIO_OPT = {
    "text": {
        "id": "text",
        "icon": "✍️",
        "description": "Inserir texto",
        "label": "✍️ Inserir texto"
    },
    "file": {
        "id": "file",
        "icon": "📚", 
        "description": "Enviar arquivo",
        "label": "📚 Enviar arquivo"
    }    
}
# --- Funções Auxiliares e de Callback ---
## tab_input
def tab0_radio_change_handler(option: str, text_input: str, file_input: Any) -> Tuple[gr.TabItem, gr.Textbox, gr.File, gr.Button]:
    """Com base na seleção do rádio e conteúdos, atualiza a interface de tab_input."""
    if option == RADIO_OPT["text"]["id"]:
        symbol = RADIO_OPT["text"]["icon"]
        return (
            gr.update(label=f"{STRINGS['TAB_0_TITLE']} {symbol}"),
            gr.update(visible=True),
            gr.update(visible=False),
            tab0_text_input_validator(text_input)
            )
    elif option == RADIO_OPT["file"]["id"]:
        symbol = RADIO_OPT["file"]["icon"]
        return (
            gr.update(label=f"{STRINGS['TAB_0_TITLE']} {symbol}"),
            gr.update(visible=False),
            gr.update(visible=True),
            tab0_file_input_validator(file_input)           
            )
    else:
        return (
            gr.skip(),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.skip()
            )

def tab0_file_input_validator(file_obj: Any) -> gr.Button:
    """
    Verifica se o arquivo carregado é válido e habilita o botão de processamento.
    Retorna um botão atualizado com base na validade do arquivo.
    """
    if file_obj is not None:
        return gr.update(interactive=True)
    else:
        return gr.update(interactive=False)
    
def tab0_text_input_validator(text: str) -> gr.Button:
    """
    Verifica se o texto inserido é válido e habilita o botão de processamento.
    Retorna um botão atualizado com base na validade do texto.
    """
    if text is not None and len(text.strip()) > 4:
        return gr.update(interactive=True)
    else:
        return gr.update(interactive=False)

def tab0_user_input_linker(radio_value: str, text_input: str, file_input) -> Tuple[gr.State, gr.TabItem, gr.Tab,]:
    """
    Captura tipo e entrada do usuário para vinculação na próxima etapa.
    Atualiza estado e navega para tab_results.
    """

    user_input = {
        "type": radio_value,
        "content": text_input if radio_value == RADIO_OPT["text"]["id"] else file_input
    }

    print(user_input)

    return (
        user_input,
        gr.update(label=STRINGS["TAB_1_TITLE"], interactive=True),
        gr.update(selected=1)
    )
   
## tab_results
def tab1_handle_status_text_change(status_text: str) -> gr.Button:
    """Atualiza o botão de criação de relatório com base no status."""
    if status_text == STRINGS["TXTBOX_STATUS_OK"]:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")

def tab1_switch_to_report_tab_and_enable_interaction() -> Tuple[gr.Tabs, gr.TabItem]:
    """Muda para a aba de relatório e a torna interativa."""
    return gr.update(selected=2), gr.update(label=STRINGS["TAB_2_TITLE"] + " ✅", interactive=True)

## tab_report
def tab2_update_dataframe_components(df_dict: Dict[str, pd.DataFrame]) -> Tuple[gr.DataFrame, gr.DataFrame, gr.DataFrame, gr.DataFrame]:
    """Atualiza os componentes visíveis de DataFrame do Gradio com novos dados."""
    print("df_dict: ", df_dict)
    return (
        gr.DataFrame(value=df_dict["group_data"]),
        gr.DataFrame(value=df_dict["group_description"]),
        gr.DataFrame(value=df_dict["individuals_data"]),
        gr.DataFrame(value=df_dict["individuals_description"])
    )

def tab2_process_report_data_wrapper(llm_response: str) -> Dict[str, pd.DataFrame]:
    """Processa os dados do relatório e retorna os DataFrames necessários."""
    print("Processando dados do relatório...\n", llm_response[:100] + "...")
    df_group, df_group_describe, df_individual_treemap, df_treemap_describe = process_report_data(llm_res=llm_response)
    
    df_dict = {
        "group_data": df_group,
        "group_description": df_group_describe,
        "individuals_data": df_individual_treemap,
        "individuals_description": df_treemap_describe
    }

    return df_dict

def tab2_report_plots_wrapper(df_dict: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
    """Chama a função de criação de gráficos com os DataFrames do relatório."""
    print("df_dict para gráficos: ", df_dict)
    df_group = df_dict["group_data"]
    df_individuals = df_dict["individuals_data"]

    pie_chart, bar_chart, tree_map = create_report_plots(df_group, df_individuals)

    plot_dict = {
        "pie_chart": pie_chart,
        "bar_chart": bar_chart,
        "tree_map": tree_map
    }

    return plot_dict

def tab2_update_plot_components(go_dict: Dict[str, go.Figure]) -> Tuple[gr.Plot, gr.Plot, gr.Plot]:
    """Atualiza os componentes visíveis de Gráfico do Gradio com novas figuras."""
    print("go_dict: ", go_dict)
    return (
        gr.Plot(value=go_dict["pie_chart"]),
        gr.Plot(value=go_dict["bar_chart"]),
        gr.Plot(value=go_dict["tree_map"])
    )

def tab2_update_download_button_component(report_file_path: Optional[str]) -> gr.DownloadButton:
    """Atualiza o componente de DownloadButton do Gradio com o caminho do PDF."""
    if report_file_path:
        return gr.update(value=report_file_path, label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ERROR"], interactive=False, variant="secondary")

def tab2_generate_report_pdf_wrapper(llm_res: str, df_dict: Dict[str, pd.DataFrame], go_dict: Dict[str, go.Figure]) -> str:
    """"Cria um pdf, retornando seu caminho."""

    temp_path = generate_report_pdf(
        llm_res=llm_res,
        df_group=df_dict["group_data"],
        df_group_describe=df_dict["group_description"],
        df_individual_treemap=df_dict["individuals_data"],
        df_treemap_describe=df_dict["individuals_description"],
        fig_pie=go_dict["pie_chart"],
        fig_bar=go_dict["bar_chart"],
        fig_tree_map=go_dict["tree_map"]
    )
    
    return temp_path
# --- Script Principal da Aplicação Gradio ---

with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    # --- States (Armazenamento de dados não visíveis) ---
    states = {
        "user_input": gr.State({
            "type": None,  # "text" ou "file"
            "content": None  # Texto ou caminho do arquivo
        }),
        "llm_response": gr.State(""),  # Resposta do LLM
        "dataframes": gr.State({
            "group_data": None,  # DataFrame com dados agrupados
            "group_description": None,  # DataFrame com descrição dos dados agrupados
            "individuals_data": None,  # DataFrame com dados individuais
            "individuals_description": None  # DataFrame com descrição dos dados individuais
        }),
        "figures": gr.State({
            "pie_chart": None,  # Figura de gráfico de pizza
            "bar_chart": None,  # Figura de gráfico de barras
            "tree_map": None  # Figura de mapa de árvore
        }),
        "report_file_path": gr.State(None),
    }

    # --- Header ---
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(f"# {STRINGS['APP_TITLE']}")
            gr.Markdown(f"{STRINGS['APP_DESCRIPTION']}")
        gr.Image(value=LOGO, height=64, container=False, show_label=False, scale=0)

    # --- Estrutura das Abas ---
    with gr.Tabs() as tabs_main_navigation:
        # --- Aba 01: Entrada ---
        with gr.TabItem(label=STRINGS["TAB_0_TITLE"], id=0) as tab_input:
            
            t0_input_type_radio = gr.Radio(
                choices=[
                    (RADIO_OPT["text"]["label"], RADIO_OPT["text"]["id"]),
                    (RADIO_OPT["file"]["label"], RADIO_OPT["file"]["id"])
                ],
                label="Selecione o tipo de entrada",
                value="text",
            )

            t0_text_input = gr.Textbox(
                label="Insira o texto para análise",
                lines=8,
                placeholder="relato de dor persistente na articulação do joelho direito...",
                visible=True
            )
            
            t0_file_input = gr.File(
                label="Carregue o documento (PDF, TXT)",
                file_types=['.pdf', '.txt'],
                visible=False
            )
            
            t0_button_process = gr.Button(
                value=STRINGS["BTN_PROCESS_LABEL"],
                interactive=False,
                variant="primary"
            )
            # Ao mudar radio, atualizar entradas e aba
            t0_input_type_radio.change(
                fn=tab0_radio_change_handler,
                inputs=[t0_input_type_radio, t0_text_input, t0_file_input],
                outputs=[tab_input, t0_text_input, t0_file_input, t0_button_process]
            )
            # Ao mudar file, verifiicar tamanho e atualizar botão de processamento            
            t0_file_input.change(
                fn=tab0_file_input_validator,
                inputs=t0_file_input,
                outputs=t0_button_process
            )
            # Ao mudar texto, verificar tamanho e atualizar botão de processamento
            t0_text_input.change(
                fn=tab0_text_input_validator,
                inputs=t0_text_input,
                outputs=t0_button_process
            )

        # --- Aba 02: Resultados ---
        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_results:
            gr.Markdown(STRINGS["TAB_1_SUBTITLE"])
            
            t1_textbox_status = gr.Textbox(
                label=STRINGS["TXTBOX_STATUS_LABEL"],
                interactive=False
            )
            
            t1_textbox_llm_response = gr.Textbox(
                label=STRINGS["TXTBOX_OUTPUT_LLM_RESPONSE_LABEL"],
                lines=15,
                interactive=False,
                placeholder=STRINGS["TXTBOX_OUTPUT_LLM_RESPONSE_PLACEHOLDER"]
            )

            t1_button_create_report = gr.Button(
                value=STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"],
                interactive=False,
                variant="secondary"
            )

            button_return_to_input_tab_from_results = gr.Button(value=STRINGS["BTN_RETURN_LABEL"], variant="secondary")

            t1_textbox_status.change(tab1_handle_status_text_change, t1_textbox_status, t1_button_create_report)

        # --- Aba 03: Relatório ---
        with gr.TabItem(STRINGS["TAB_2_TITLE"] + " 🔒", interactive=False, id=2) as tab_report:
            gr.Markdown(STRINGS["TAB_2_SUBTITLE"])
            
            with gr.Row():
                t2_dataframe_grouped_data = gr.DataFrame(label=STRINGS["DF_GROUP_DATA"])
                t2_dataframe_grouped_description = gr.DataFrame(label=STRINGS["DF_GROUP_DESC"])
            
            with gr.Row():
                t2_dataframe_individual_data = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DATA"])
                t2_dataframe_individual_description = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DESC"])
            
            t2_plot_pie_chart = gr.Plot(label=STRINGS["PLOT_PIE_LABEL"])
            
            t2_plot_bar_chart = gr.Plot(label=STRINGS["PLOT_BAR_LABEL"])
            
            t2_plot_tree_map = gr.Plot(label=STRINGS["PLOT_TREE_LABEL"])
            
            t2_download_button_report_pdf = gr.DownloadButton(
                label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_DISABLED"],
                interactive=False,
                variant="secondary"
            )
            
            button_return_to_input_tab_from_report = gr.Button(value=STRINGS["BTN_RETURN_LABEL"], variant="secondary")

    # --- Lógica de Eventos e Conexões ---

    t0_button_process.click(
        fn=tab0_user_input_linker,
        inputs=[t0_input_type_radio, t0_text_input, t0_file_input],
        outputs=[states["user_input"], tab_results, tabs_main_navigation]
    ).then(
        fn=process_inputs_to_api,
        inputs=states["user_input"],
        outputs=[
            t1_textbox_status, t1_textbox_llm_response, tabs_main_navigation, tab_results
        ]
    )
    # Armazena a resposta do LLM no state quando ela for atualizada
    t1_textbox_llm_response.change(lambda r: r, t1_textbox_llm_response, states["llm_response"])

    t1_button_create_report.click(
        fn=tab1_switch_to_report_tab_and_enable_interaction,
        outputs=[tabs_main_navigation, tab_report]
    ).then(
        fn=tab2_process_report_data_wrapper,
        inputs=states["llm_response"],
        outputs=states["dataframes"]
    ).then(
        fn=tab2_update_dataframe_components,
        inputs=states["dataframes"],
        outputs=[
            t2_dataframe_grouped_data, t2_dataframe_grouped_description,
            t2_dataframe_individual_data, t2_dataframe_individual_description
            ]
    ).then(
        fn=tab2_report_plots_wrapper,
        inputs=states["dataframes"],
        outputs=states["figures"]
    ).then(
        fn=tab2_update_plot_components,
        inputs=states["figures"],
        outputs=[
            t2_plot_pie_chart,
            t2_plot_bar_chart,
            t2_plot_tree_map
        ]
    ).then(
        fn=tab2_generate_report_pdf_wrapper,
        inputs=[
            states["llm_response"],
            states["dataframes"],
            states["figures"],
        ],
        outputs=states["report_file_path"]
    ).then(
        fn=tab2_update_download_button_component,
        inputs=states["report_file_path"],
        outputs=t2_download_button_report_pdf
    )

    # Botões de Navegação "Voltar"
    button_return_to_input_tab_from_results.click(lambda: gr.update(selected=0), outputs=tabs_main_navigation)
    button_return_to_input_tab_from_report.click(lambda: gr.update(selected=0), outputs=tabs_main_navigation)

if __name__ == "__main__":
    print("Executando a aplicação Gradio...")
    interface.launch()
