# pages/main/view.py
import os
import gradio as gr

from .scripts import RADIO_OPT, InputTabFn, ResultsTabFn, ReportTabFn
from .strings import STRINGS

# --- Constantes ---
LOGO = os.path.join(os.getcwd(), "static", "images", "logo.jpg")

with gr.Blocks(title=STRINGS["APP_TITLE"]) as interface:
    # --- States (Armazenamento de dados não visíveis) ---
    states = {
        "user_input": gr.State({
            "type": None,  # "text" ou "file"
            "content": None  # Texto ou caminho do arquivo
        }),
        "llm_response": gr.State(""),
        "dataframes": gr.State({
            "group_data": None,
            "group_description": None,
            "individuals_data": None,
            "individuals_description": None
        }),
        "figures": gr.State({
            "pie_chart": None,
            "bar_chart": None,
            "tree_map": None
        }),
        "report_file_path": gr.State(None),
        "start_time": gr.State(None),
    }

    # --- Header ---
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(f"# {STRINGS['APP_TITLE']}")
            gr.Markdown(f"{STRINGS['APP_DESCRIPTION']}")
        gr.Image(value=LOGO, height=64, container=False, show_label=False, show_download_button=False, scale=0)

    # --- Estrutura das Abas ---
    with gr.Tabs() as tabs_main_navigation:
        # --- Aba 01: Entrada ---
        with gr.TabItem(label=f"{STRINGS['TAB_0_TITLE']} {RADIO_OPT['text']['icon']}", id=0) as tab_input:
            
            t0_input_type_radio = gr.Radio(
                choices=[
                    (RADIO_OPT["text"]["label"], RADIO_OPT["text"]["id"]),
                    (RADIO_OPT["file"]["label"], RADIO_OPT["file"]["id"])
                ],
                label=STRINGS["RADIO_INPUT_TYPE_LABEL"],
                value="text",
            )

            t0_text_input = gr.Textbox(
                label=STRINGS["TXTBOX_INPUT_PHRASES_LABEL"],
                lines=8,
                placeholder=STRINGS["TXTBOX_INPUT_PHRASES_PLACEHOLDER"],
                visible=True
            )
            
            t0_file_input = gr.File(
                label=STRINGS["FILE_INPUT_LABEL"],
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
                fn=InputTabFn.update_input_visibility,
                inputs=[t0_input_type_radio, t0_text_input, t0_file_input],
                outputs=[tab_input, t0_text_input, t0_file_input, t0_button_process]
            )
            # Ao mudar file, verifiicar tamanho e atualizar botão de processamento            
            t0_file_input.change(
                fn=InputTabFn.file_input_validator,
                inputs=t0_file_input,
                outputs=t0_button_process
            )
            # Ao mudar texto, verificar tamanho e atualizar botão de processamento
            t0_text_input.change(
                fn=InputTabFn.text_input_validator,
                inputs=t0_text_input,
                outputs=t0_button_process
            )

        # --- Aba 02: Resultados ---
        with gr.TabItem(STRINGS["TAB_1_TITLE"] + " 🔒", interactive=False, id=1) as tab_results:
            gr.Markdown(STRINGS["TAB_1_SUBTITLE"])

            t1_timer_display = gr.Textbox(
                label=STRINGS["TXTBOX_TIMER_LABEL"],
                value="0.000",
                interactive=False,
            )

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

            t1_textbox_status.change(
                fn=ResultsTabFn.handle_status_text_change,
                inputs=t1_textbox_status,
                outputs=t1_button_create_report
            )

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
        fn=InputTabFn.handle_process_button_click,
        inputs=[t0_input_type_radio, t0_text_input, t0_file_input],
        outputs=[states["user_input"], tab_results, tabs_main_navigation]
    ).then(
        # Inicia o timer e armazena o tempo de início
        fn=ResultsTabFn.start_timer,
        inputs=None,
        outputs=states["start_time"]
    ).then(
        # Processa a API
        fn=ResultsTabFn.process_inputs_to_api,
        inputs=states["user_input"],
        outputs=[
            t1_textbox_status, t1_textbox_llm_response, tabs_main_navigation, tab_results
        ]
    ).then(
        # Quando a API terminar, calcula e exibe o tempo final
        fn=ResultsTabFn.stop_timer,
        inputs=states["start_time"],
        outputs=t1_timer_display
    )
    # Armazena a resposta do LLM no state quando ela for atualizada
    t1_textbox_llm_response.change(lambda r: r, t1_textbox_llm_response, states["llm_response"])

    t1_button_create_report.click(
        fn=ResultsTabFn.switch_to_report_tab,
        outputs=[tabs_main_navigation, tab_report]
    ).then(
        fn=ReportTabFn.process_report_data_wrapper,
        inputs=states["llm_response"],
        outputs=states["dataframes"]
    )

    # Ao 'dataframes' mudar, atualizar os componentes do dataframe na UI.
    states["dataframes"].change(
        fn=ReportTabFn.update_dataframe_components,
        inputs=states["dataframes"],
        outputs=[
            t2_dataframe_grouped_data, t2_dataframe_grouped_description,
            t2_dataframe_individual_data, t2_dataframe_individual_description
        ]
    ).then(
        fn=ReportTabFn.report_plots_wrapper,
        inputs=states["dataframes"],
        outputs=states["figures"]
    )

    # Ao 'figures' mudar, atualizar os componentes de plot na UI.
    states["figures"].change(
        fn=ReportTabFn.update_plot_components,
        inputs=states["figures"],
        outputs=[
            t2_plot_pie_chart,
            t2_plot_bar_chart,
            t2_plot_tree_map
        ]
    ).then(
        fn=ReportTabFn.generate_report_pdf_wrapper,
        inputs=[
            states["llm_response"],
            states["dataframes"],
            states["figures"],
        ],
        outputs=states["report_file_path"]
    )

    # Ao 'report_file_path' mudar, atualizar o botão de download.
    states["report_file_path"].change(
        fn=ReportTabFn.update_download_button_component,
        inputs=states["report_file_path"],
        outputs=t2_download_button_report_pdf
    )

    # Botões de Navegação "Voltar"
    button_return_to_input_tab_from_results.click(lambda: gr.update(selected=0), outputs=tabs_main_navigation)
    button_return_to_input_tab_from_report.click(lambda: gr.update(selected=0), outputs=tabs_main_navigation)

# --- Rodapé da IA ---
    gr.HTML("""
    <style>
        .rodape-ia {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            text-align: center;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 14px;
            color: #333;
            z-index: 1000;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
        }
    </style>
    <div class="rodape-ia">
        Atenção: Esta aplicação utiliza inteligência artificial para a vinculação CIF. Por isso, é fundamental que você revise as informações apresentadas.
    </div>
    """)

if __name__ == "__main__":
    print("Executando a aplicação Gradio...")
    interface.launch()
