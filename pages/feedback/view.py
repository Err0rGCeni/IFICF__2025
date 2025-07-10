# pages/feedback/view.py
import gradio as gr

# Importa as funções de lógica e as strings necessárias
from .scripts import submit_feedback, update_submit_button_state, reset_form_fields
from .strings import STRINGS

# --- Constantes de Interface ---
DROP_CHOICES_LIST = ["Erro & Bug", "Sugestão", "Elogio", "Outro"]

# --- Definição da Interface Gradio ---
with gr.Blocks() as interface:
    gr.Markdown(STRINGS["TITLE"])
    gr.Markdown(STRINGS["SUBTITLE"])
    gr.Markdown(STRINGS["DESCRIPTION"])

    with gr.Row():
        type_input = gr.Dropdown(
            label=STRINGS["DROP_LABEL"],
            choices=DROP_CHOICES_LIST,
            value="Sugestão",
            interactive=True,
            scale=1
        )
    
    comment_input = gr.Textbox(
        label=STRINGS["COMMENT_LABEL"],
        placeholder=STRINGS["COMMENT_PLACEHOLDER"],
        lines=5
    )

    submit_button = gr.Button(STRINGS["BTN_SUBMIT_LABEL"], variant="secondary", interactive=False)

    output_message = gr.Textbox(label="Status", value=STRINGS["OUTPUT_IDLE"], interactive=False)

    # --- Listeners de Eventos (conectando UI com a lógica) ---
    comment_input.change(
        fn=update_submit_button_state,
        inputs=comment_input,
        outputs=submit_button,
        api_name=False
    )

    submit_button.click(
        fn=submit_feedback,
        inputs=[type_input, comment_input],
        outputs=output_message
    ).then(
        fn=reset_form_fields,
        inputs=output_message,
        outputs=[comment_input, type_input, submit_button, output_message],
        api_name=False
    )

if __name__ == "__main__":
    interface.launch()