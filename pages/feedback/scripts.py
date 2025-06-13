import datetime
import gspread
import os
from dotenv import load_dotenv
from typing import Optional

# Importa as strings para usar mensagens padronizadas
from .strings import STRINGS

# --- Configuração Inicial do Google Sheets ---
load_dotenv()

# Obtém o caminho do arquivo da chave de serviço da variável de ambiente
service_account_key_path: Optional[str] = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
spreadsheet_name: Optional[str] = os.getenv('GOOGLE_SHEETS_NAME')

# Variáveis globais para armazenar a conexão com o Google Sheets
# São inicializadas como None e configuradas pela função _initialize_google_sheets()
gc: Optional[gspread.Client] = None
worksheet: Optional[gspread.Worksheet] = None
initialization_error_message: Optional[str] = None

def _initialize_google_sheets() -> bool:
    """
    Inicializa a conexão com o Google Sheets (gspread) e a planilha (worksheet) uma única vez.

    Esta função tenta estabelecer a conexão com o Google Sheets usando as credenciais
    fornecidas pelas variáveis de ambiente. Se a conexão for bem-sucedida, ela armazena
    as referências globais 'gc' e 'worksheet'. Em caso de falha, armazena uma mensagem
    de erro em 'initialization_error_message' e imprime no console.

    Returns:
        bool: True se a conexão e o acesso à planilha foram estabelecidos com sucesso,
              False caso contrário.
    """
    global gc, worksheet, initialization_error_message

    if initialization_error_message:
        return False

    if gc and worksheet:
        return True

    if not service_account_key_path:
        initialization_error_message = STRINGS["ERROR_ENV_KEY_PATH_NOT_DEFINED"]
        print(initialization_error_message)
        return False

    if not spreadsheet_name:
        initialization_error_message = STRINGS["ERROR_ENV_SHEET_NAME_NOT_DEFINED"]
        print(initialization_error_message)
        return False

    try:
        gc = gspread.service_account(filename=service_account_key_path)
    except Exception as e:
        initialization_error_message = f"{STRINGS['ERROR_LOAD_SERVICE_KEY']} {e}." # Verifique o caminho e o conteúdo do arquivo JSON.
        print(initialization_error_message)
        return False

    try:
        sh = gc.open(spreadsheet_name)
        worksheet = sh.sheet1
        print(STRINGS["INFO_CONNECTION_SUCCESS"])
        return True
    except gspread.exceptions.SpreadsheetNotFound:
        initialization_error_message = f"{STRINGS['ERROR_SHEET_NOT_FOUND']} {spreadsheet_name}." # Verifique o nome e o compartilhamento com a conta de serviço.
        print(initialization_error_message)
        return False
    except Exception as e:
        initialization_error_message = f"{STRINGS['ERROR_ACCESS_SHEET']} {e}."  #  Verifique permissões ou o ID da planilha.
        print(initialization_error_message)
        return False

# Chama a função de inicialização uma única vez quando o módulo é carregado.
_initialize_google_sheets()

def submit_feedback_and_handle_errors(feedback_type: str, comment_text: str) -> str:
    """
    Processa o feedback do usuário, valida a entrada e tenta enviá-lo para
    o Google Sheets.

    Gerencia erros de validação da entrada do usuário e erros na conexão
    ou escrita no Google Sheets, retornando mensagens amigáveis para a UI.

    Args:
        feedback_type (str): O tipo de feedback selecionado pelo usuário (ex: "Bug", "Sugestão").
        comment_text (str): O texto do comentário ou descrição do feedback.

    Returns:
        str: Uma mensagem de status para ser exibida na interface do usuário (Gradio),
             indicando sucesso ou erro.
    """
    # 1. Validação de campos do formulário Gradio
    if not comment_text.strip():
        return STRINGS["ERROR_COMMENT_EMPTY"]
    if not feedback_type:
        return STRINGS["ERROR_TYPE_EMPTY"]

    # 2. Verificação de status da inicialização do Google Sheets
    global gc, worksheet, initialization_error_message

    if initialization_error_message:
        return f"{STRINGS['ERROR_SERVICE_UNAVAILABLE_CONFIG']} {initialization_error_message}"
    
    if not gc or not worksheet:
        if not _initialize_google_sheets():
            return f"{STRINGS['ERROR_SERVICE_UNAVAILABLE_CONNECTION']} {initialization_error_message}"

    # Gera o timestamp atual no formato desejado.
    timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tenta adicionar a linha à planilha do Google Sheets.
    try:
        worksheet.append_row([timestamp, feedback_type, comment_text]) # type: ignore [union-attr]
        return STRINGS["OUTPUT_SUCCESS"]
    except Exception as e:
        return f"{STRINGS['OUTPUT_ERROR']} {e}. Tente novamente mais tarde."