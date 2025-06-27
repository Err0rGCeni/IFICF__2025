# pages/main/view.py
import os
import gradio as gr
from typing import Tuple, Optional, Any

from utils.report_creation import process_report_data, create_report_plots, generate_report_pdf
from .scripts import process_inputs_to_api
from .strings import STRINGS
from .tab01_input import create_input_tabs
from .tab02_results import create_tab_results
# MODIFICAÇÃO: A importação de create_tab_report permanece a mesma
from .tab03_report import create_tab_report

img1 = os.path.join(os.getcwd(), "static", "images", "logo.jpg")

# --- Funções Auxiliares (Apenas Lógica Geral da View) ---
def _update_process_button_state(
    input_type: str, file_input: Optional[Any], text_input: str
) -> gr.Button:
    """
    Atualiza o estado do botão 'Processar' com base na seleção e no preenchimento dos campos.

    Args:
        input_type: O valor selecionado no rádio ("Vinculação de documento 📙" ou "Vinculação de texto ✍️").
        file_input: O objeto de arquivo do componente gr.File (None se vazio).
        text_input: O conteúdo do componente gr.Textbox.

    Returns:
        Um gr.Button atualizado (estado interativo e valor/label).
    """
    base_label = STRINGS["BTN_PROCESS_INPUT_LABEL_ENABLED"]

    if input_type == "Vinculação de documento 📙":
        if file_input is not None:
            # Habilitado se um arquivo for carregado
            return gr.update(value=f"{base_label} 📙", interactive=True)
        else:
            # Desabilitado se nenhum arquivo for carregado
            return gr.update(value=f"{base_label} 📙", interactive=False)

    elif input_type == "Vinculação de texto ✍️":
        if text_input and len(text_input.strip()) >= 3:
            # Habilitado se o texto tiver 3 ou mais caracteres
            return gr.update(value=f"{base_label} ✍️", interactive=True)
        else:
            # Desabilitado se o texto for muito curto
            return gr.update(value=f"{base_label} ✍️", interactive=False)
            
    # Estado padrão/inicial: desabilitado
    return gr.update(value=base_label, interactive=False)


def _switch_to_report_tab_and_enable_interaction() -> Tuple[gr.Tabs, gr.TabItem]:
    """Muda para a aba de relatório e a torna interativa."""
    return gr.update(selected=2), gr.update(label=STRINGS["TAB_2_TITLE"] + " ✅", interactive=True)

# --- Construção da Interface Gradio ---
with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    # --- States (armazenam dados entre interações) ---
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

    # --- Estrutura das Abas e Chamada às Funções Modulares ---
    components = {}
    with gr.Tabs() as tabs_main_navigation:
        with gr.TabItem(STRINGS["TAB_0_TITLE"], id=0) as tab_input:
            components.update(create_input_tabs())
            button_process_input = gr.Button(
                value=STRINGS["BTN_PROCESS_INPUT_LABEL_ENABLED"],
                interactive=False,
                variant="primary"
            )
            components["button_process_input"] = button_process_input

        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_results:
            components.update(create_tab_results())
            components["tab_item_processing_results"] = tab_results

        with gr.TabItem(STRINGS["TAB_2_TITLE"] + " 🔒", interactive=False, id=2) as tab_report:
            report_elements = create_tab_report()
            components.update(report_elements["components"])
            components["tab_item_report_visualization"] = tab_report

    listeners = [
        components["input_type_radio"],
        components["file_input"],
        components["text_input"]
    ]
    
    for component in listeners:
        # Usamos .change() para texto/arquivo e .select() para o rádio para melhor semântica
        event = component.select if isinstance(component, gr.Radio) else component.change
        event(
            fn=_update_process_button_state,
            inputs=[
                components["input_type_radio"],
                components["file_input"],
                components["text_input"]
            ],
            outputs=components["button_process_input"]
        )

    # ... O click do button_process_input e o change do textbox_output_llm_response permanecem os mesmos ...
    components["button_process_input"].click(
        fn=process_inputs_to_api,
        inputs=[
            components["text_input"],
            components["file_input"]
        ],
        outputs=[
            components["textbox_output_status"],
            components["textbox_output_llm_response"],
            tabs_main_navigation,
            components["tab_item_processing_results"]
        ]
    )
    
    components["textbox_output_llm_response"].change(
        fn=lambda response_text: response_text,
        inputs=components["textbox_output_llm_response"],
        outputs=states["llm_response"]
    )

    # Fluxo encadeado para gerar o relatório
    components["button_create_report"].click(
        fn=_switch_to_report_tab_and_enable_interaction,
        outputs=[tabs_main_navigation, components["tab_item_report_visualization"]]
    ).then(
        fn=process_report_data,
        inputs=[states["llm_response"]],
        outputs=list(states.values())[:4]
    ).then(
        # MODIFICAÇÃO: Usamos a função fornecida por report_elements
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
        # MODIFICAÇÃO: Usamos a função fornecida por report_elements
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
        # MODIFICAÇÃO: Usamos a função fornecida por report_elements
        fn=report_elements["update_fns"]["download"],
        inputs=[states["report_file_path"]],
        outputs=[components["download_button_report_pdf"]]
    )

    # ... Eventos de "Voltar" permanecem os mesmos ...
    components["button_return_to_input_tab_from_results"].click(fn=lambda: gr.update(selected=0), outputs=tabs_main_navigation)
    components["button_return_to_input_tab_from_report"].click(fn=lambda: gr.update(selected=0), outputs=tabs_main_navigation)

if __name__ == "__main__":
    print("Executando a aplicação Gradio...")
    interface.launch()