# pages/feedback/scripts.py
import datetime
import gradio as gr

from utils.apis import gsheets
from .strings import STRINGS

# --- Funções de Lógica de UI (Movidas de view.py) ---

def update_submit_button_state(comment_text: str) -> gr.update:
    """
    Atualiza o estado do botão de envio com base no texto do comentário.
    """
    if len(comment_text.strip()) >= 3:
        return gr.update(interactive=True, variant="primary")
    else:
        return gr.update(interactive=False, variant="secondary")

def reset_form_fields(status_message: str) -> tuple:
    """
    Reseta os campos do formulário para seus estados iniciais após o envio.
    """
    return (
        gr.update(value=""),
        gr.update(value="Sugestão"),
        gr.update(interactive=False, variant="secondary"),
        gr.update(value=status_message)
    )

# --- Função Acopladora / Lógica de Dados ---

def submit_feedback(feedback_type: str, comment_text: str) -> str:
    """
    Processa o feedback do usuário, valida a entrada e utiliza o módulo gsheets
    para enviá-lo. Funciona como um "acoplador" entre a UI e a API.

    Args:
        feedback_type (str): O tipo de feedback selecionado.
        comment_text (str): O comentário do usuário.

    Returns:
        str: Uma mensagem de status para ser exibida na UI.
    """
    # 1. Validação da entrada do formulário
    if not comment_text.strip():
        return STRINGS["ERROR_COMMENT_EMPTY"]
    if not feedback_type:
        return STRINGS["ERROR_TYPE_EMPTY"]

    # 2. Preparação dos dados para a planilha
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_data = [timestamp, feedback_type, comment_text]

    # 3. Chamada ao módulo da API para adicionar a linha
    error = gsheets.append_row(row_data)

    # 4. Retorno de mensagem de sucesso ou erro para a UI
    if error:
        print(f"Erro retornado pela API gsheets: {error}")
        return f"{STRINGS['OUTPUT_ERROR']}. Tente novamente mais tarde."
    else:
        return STRINGS["OUTPUT_SUCCESS"]