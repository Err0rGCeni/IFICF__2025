# pages/main/tab03_report.py
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, Optional
from .strings import STRINGS

# --- Funções de Atualização (Lógica Interna da Aba) ---

def update_dataframe_components(
    group_data_df: Optional[pd.DataFrame],
    group_description_df: Optional[pd.DataFrame],
    individuals_data_df: Optional[pd.DataFrame],
    individuals_description_df: Optional[pd.DataFrame]
) -> Tuple[gr.DataFrame, gr.DataFrame, gr.DataFrame, gr.DataFrame]:
    """Atualiza os componentes visíveis de DataFrame do Gradio com novos dados."""
    return (
        gr.DataFrame(value=group_data_df),
        gr.DataFrame(value=group_description_df),
        gr.DataFrame(value=individuals_data_df),
        gr.DataFrame(value=individuals_description_df)
    )

def update_plot_components(
    pie_chart_figure: Optional[go.Figure],
    bar_chart_figure: Optional[go.Figure],
    tree_map_figure: Optional[go.Figure]
) -> Tuple[gr.Plot, gr.Plot, gr.Plot]:
    """Atualiza os componentes visíveis de Gráfico do Gradio com novas figuras."""
    return (
        gr.Plot(value=pie_chart_figure),
        gr.Plot(value=bar_chart_figure),
        gr.Plot(value=tree_map_figure)
    )

def update_download_button_component(report_file_path: Optional[str]) -> gr.DownloadButton:
    """Atualiza o componente de DownloadButton do Gradio com o caminho do PDF."""
    if report_file_path:
        return gr.update(value=report_file_path, label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ERROR"], interactive=False, variant="secondary")

def create_tab_report() -> dict:
    """
    Cria a aba de relatório e retorna um dicionário contendo
    os componentes da UI e as funções para atualizá-los.
    """
    gr.Markdown(STRINGS["TAB_2_SUBTITLE"])

    with gr.Row():
        dataframe_display_grouped_data = gr.DataFrame(label=STRINGS["DF_GROUP_DATA"])
        dataframe_display_grouped_description = gr.DataFrame(label=STRINGS["DF_GROUP_DESC"])
    # ... (outros componentes são criados aqui como antes) ...
    with gr.Row():
        dataframe_display_individual_data = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DATA"])
        dataframe_display_individual_description = gr.DataFrame(label=STRINGS["DF_INDIVIDUAL_DESC"])

    plot_display_pie_chart = gr.Plot(label=STRINGS["PLOT_PIE_LABEL"])
    plot_display_bar_chart = gr.Plot(label=STRINGS["PLOT_BAR_LABEL"])
    plot_display_tree_map = gr.Plot(label=STRINGS["PLOT_TREE_LABEL"])

    download_button_report_pdf = gr.DownloadButton(
        label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_DISABLED"],
        interactive=False,
        variant="secondary"
    )

    button_return_to_input_tab_from_report = gr.Button(
        STRINGS["BTN_RETURN_LABEL"],
        variant="secondary"
    )

    # MODIFICAÇÃO: Retornamos um dicionário estruturado
    return {
        "components": {
            "dataframe_display_grouped_data": dataframe_display_grouped_data,
            "dataframe_display_grouped_description": dataframe_display_grouped_description,
            "dataframe_display_individual_data": dataframe_display_individual_data,
            "dataframe_display_individual_description": dataframe_display_individual_description,
            "plot_display_pie_chart": plot_display_pie_chart,
            "plot_display_bar_chart": plot_display_bar_chart,
            "plot_display_tree_map": plot_display_tree_map,
            "download_button_report_pdf": download_button_report_pdf,
            "button_return_to_input_tab_from_report": button_return_to_input_tab_from_report
        },
        "update_fns": {
            "dataframes": update_dataframe_components,
            "plots": update_plot_components,
            "download": update_download_button_component
        }
    }