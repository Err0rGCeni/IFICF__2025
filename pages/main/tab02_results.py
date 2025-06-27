# pages/main/tab02_results.py
import gradio as gr
from .strings import STRINGS

def _handle_status_text_change(status_text: str) -> gr.Button:
    """
    Listener for the status textbox. Updates the report creation button
    based on the content of the status textbox.
    """
    if status_text == STRINGS["TXTBOX_STATUS_OK"]:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
    else:
        return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")

def create_tab_results():
    """
    Cria e retorna um dicionário com os componentes da UI para a aba de resultados.
    """
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

    button_create_report = gr.Button(
        STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], 
        interactive=False, 
        variant="secondary"
    )
    
    button_return_to_input_tab_from_results = gr.Button(
        STRINGS["BTN_RETURN_LABEL"], 
        variant="secondary"
    )

    # Evento para habilitar o botão de criar relatório
    textbox_output_status.change(
        fn=_handle_status_text_change,
        inputs=textbox_output_status,
        outputs=button_create_report
    )

    return {
        "textbox_output_status": textbox_output_status,
        "textbox_output_llm_response": textbox_output_llm_response,
        "button_create_report": button_create_report,
        "button_return_to_input_tab_from_results": button_return_to_input_tab_from_results
    }