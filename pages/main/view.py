# pages/main/view.py
import os
import gradio as gr
from typing import Tuple, Any

from utils.report.report_creation import generate_report_pdf
from utils.report.graph_creation import create_report_plots
from utils.report.dataframe_creation import process_report_data

from .scripts import process_inputs_to_api
from .strings import STRINGS
from .tab01_input import create_input_components
from .tab02_results import create_tab_results
from .tab03_report import create_tab_report

img1 = os.path.join(os.getcwd(), "static", "images", "logo.jpg")

def _switch_to_report_tab_and_enable_interaction() -> Tuple[gr.Tabs, gr.TabItem]:
    """Muda para a aba de relatório e a torna interativa."""
    return gr.update(selected=2), gr.update(label=STRINGS["TAB_2_TITLE"] + " ✅", interactive=True)

with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    # --- States ---
    states = {
        "dataframe_group": gr.State(None),
        "dataframe_group_description": gr.State(None),
        "dataframe_individuals": gr.State(None),
        "dataframe_individuals_description": gr.State(None),
        "figure_pie_chart": gr.State(None),
        "figure_bar_chart": gr.State(None),
        "figure_tree_map": gr.State(None),
        "report_file_path": gr.State(None),
        "llm_response": gr.State(None)
    }

    # --- Header ---
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(f"# {STRINGS['APP_TITLE']}")
            gr.Markdown(f"{STRINGS['APP_DESCRIPTION']}")
        gr.Image(value=img1, height=64, container=False, show_label=False, scale=0)

    # --- Estrutura das Abas ---
    components = {}
    with gr.Tabs() as tabs_main_navigation:
        with gr.TabItem(STRINGS["TAB_0_TITLE"], id=0) as tab_input:
            # Cria os componentes de entrada da Tab 1
            components.update(create_input_components())

        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_results:
            components.update(create_tab_results())
            components["tab_item_processing_results"] = tab_results

        with gr.TabItem(STRINGS["TAB_2_TITLE"] + " 🔒", interactive=False, id=2) as tab_report:
            report_elements = create_tab_report()
            components.update(report_elements["components"])
            components["tab_item_report_visualization"] = tab_report

    # --- Ações dos Botões de Processamento ---

    # Saídas comuns para ambos os botões de processamento
    common_api_outputs = [
        components["textbox_output_status"],
        components["textbox_output_llm_response"],
        tabs_main_navigation,
        components["tab_item_processing_results"]
    ]

    # Botão para processar ARQUIVO
    components["button_process_file"].click(
        fn=process_inputs_to_api,
        # Inputs: (None para texto, objeto de arquivo)
        inputs=[gr.State(None), components["file_input"]],
        outputs=common_api_outputs
    )

    # Botão para processar TEXTO
    components["button_process_text"].click(
        fn=process_inputs_to_api,
        # Inputs: (string de texto, None para arquivo)
        inputs=[components["text_input"], gr.State(None)],
        outputs=common_api_outputs
    )

    components["textbox_output_llm_response"].change(
        fn=lambda response_text: response_text,
        inputs=components["textbox_output_llm_response"],
        outputs=states["llm_response"]
    )

    # --- Fluxo de Geração de Relatório ---
    components["button_create_report"].click(
        fn=_switch_to_report_tab_and_enable_interaction,
        outputs=[tabs_main_navigation, components["tab_item_report_visualization"]]
    ).then(
        fn=process_report_data,
        inputs=[states["llm_response"]],
        outputs=list(states.values())[:4]
    ).then(
        fn=report_elements["update_fns"]["dataframes"],
        inputs=list(states.values())[:4],
        outputs=[
            components["dataframe_display_grouped_data"],
            components["dataframe_display_grouped_description"],
            components["dataframe_display_individual_data"],
            components["dataframe_display_individual_description"],
        ]
    ).then(
        fn=create_report_plots,
        inputs=[states["dataframe_group"], states["dataframe_individuals"]],
        outputs=[states["figure_pie_chart"], states["figure_bar_chart"], states["figure_tree_map"]]
    ).then(
        fn=report_elements["update_fns"]["plots"],
        inputs=[states["figure_pie_chart"], states["figure_bar_chart"], states["figure_tree_map"]],
        outputs=[
            components["plot_display_pie_chart"],
            components["plot_display_bar_chart"],
            components["plot_display_tree_map"]
        ]
    ).then(
        fn=generate_report_pdf,
        inputs=[
           states["llm_response"],
           states["dataframe_group"],
           states["dataframe_group_description"],
           states["dataframe_individuals"],
           states["dataframe_individuals_description"],
           states["figure_pie_chart"],
           states["figure_bar_chart"],
           states["figure_tree_map"]
        ],
        outputs=[states["report_file_path"]]
    ).then(
        fn=report_elements["update_fns"]["download"],
        inputs=[states["report_file_path"]],
        outputs=[components["download_button_report_pdf"]]
    )

    # --- Botões de Navegação "Voltar" ---
    components["button_return_to_input_tab_from_results"].click(fn=lambda: gr.update(selected=0), outputs=tabs_main_navigation)
    components["button_return_to_input_tab_from_report"].click(fn=lambda: gr.update(selected=0), outputs=tabs_main_navigation)

if __name__ == "__main__":
    print("Executando a aplicação Gradio...")
    interface.launch()