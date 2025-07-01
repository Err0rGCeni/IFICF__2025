# pages/feedback/view.py
import gradio as gr

from .scripts import submit_feedback_and_handle_errors
from .strings import STRINGS

# --- Constantes de Interface ---
DROP_CHOICES_LIST = ["Erro & Bug", "Sugestão", "Elogio", "Outro"]

# --- Funções Auxiliares (Listeners e Controladores de UI) ---
def _update_submit_button_state(comment_text: str) -> gr.update:
    """
    Atualiza o estado (habilitado/desabilitado e cor) do botão de envio
    com base no comprimento do texto do comentário.

    O botão é habilitado e se torna 'primary' se o comentário tiver
    ao menos 3 caracteres (após remover espaços). Caso contrário,
    permanece desabilitado e 'secondary'.
    """
    if len(comment_text.strip()) >= 3:
        return gr.update(interactive=True, variant="primary")
    else:
        return gr.update(interactive=False, variant="secondary")

def _reset_form_and_button(message: str) -> tuple[gr.Textbox, gr.Dropdown, gr.Button, gr.Textbox]:
    """
    Reseta os campos do formulário (comentário e tipo de feedback) e o botão de envio
    para seus estados iniciais após o envio do feedback.

    Mantém a mensagem de status exibida para o usuário.
    """
    return (
        gr.update(value=""),  # Reseta o campo de comentário
        gr.update(value="Sugestão"), # Reseta o dropdown para o valor padrão
        gr.update(interactive=False, variant="secondary"), # Desabilita e muda a cor do botão
        gr.update(value=message) # Repassa a mensagem de saída para o usuário
    )

# --- Aplicação Gradio ---
with gr.Blocks() as interface:
    gr.Markdown(STRINGS["TITLE"])
    gr.Markdown(STRINGS["SUBTITLE"])
    gr.Markdown(STRINGS["DESCRIPTION"])

    type_input = gr.Dropdown(
        label=STRINGS["DROP_LABEL"],
        choices=DROP_CHOICES_LIST,
        value="Sugestão",
        interactive=True
    )

    comment_input = gr.Textbox(
        label=STRINGS["COMMENT_LABEL"],
        placeholder=STRINGS["COMMENT_PLACEHOLDER"],
        lines=5
    )

    submit_button = gr.Button(STRINGS["BTN_SUBMIT_LABEL"], variant="secondary", interactive=False)

    output_message = gr.Textbox(label="Status", value=STRINGS["OUTPUT_IDLE"], interactive=False)

    # --- Listeners de Eventos ---
    comment_input.change(
        fn=_update_submit_button_state,
        inputs=comment_input,
        outputs=submit_button,
        api_name=False
    )

    submit_button.click(
        fn=submit_feedback_and_handle_errors,
        inputs=[type_input, comment_input],
        outputs=output_message
    ).then(
        fn=_reset_form_and_button,
        inputs=output_message,
        outputs=[comment_input, type_input, submit_button, output_message],
        api_name=False
    )

if __name__ == "__main__":
    interface.launch()