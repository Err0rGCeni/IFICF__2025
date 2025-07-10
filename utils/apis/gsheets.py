# utils/apis/gsheets.py
import gspread
import os
from dotenv import load_dotenv
from typing import Optional, List, Any

# --- Configuração e Conexão com a API ---
load_dotenv()

# Carrega as configurações das variáveis de ambiente
SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
SPREADSHEET_NAME: Optional[str] = os.getenv('GOOGLE_SHEETS_NAME')

# Variáveis globais para "cachear" a conexão e evitar reinicializações
_gc_client: Optional[gspread.Client] = None
_worksheet: Optional[gspread.Worksheet] = None
_initialization_error: Optional[str] = None

def _initialize_connection() -> Optional[str]:
    """
    Inicializa e armazena a conexão com o Google Sheets.

    Tenta conectar-se usando as credenciais do ambiente. Se a conexão for bem-sucedida,
    armazena o cliente e a planilha em variáveis globais. Em caso de falha, armazena
    a mensagem de erro para evitar novas tentativas.

    Returns:
        Optional[str]: Uma string com a mensagem de erro em caso de falha, ou None se bem-sucedido.
    """
    global _gc_client, _worksheet, _initialization_error

    # Se já houve uma tentativa de conexão (bem-sucedida ou não), retorna o resultado
    if _gc_client and _worksheet:
        return None
    if _initialization_error:
        return _initialization_error

    # Validação das variáveis de ambiente
    if not SERVICE_ACCOUNT_KEY_PATH:
        _initialization_error = "A variável de ambiente 'SERVICE_ACCOUNT_KEY_PATH' não foi definida."
        return _initialization_error
    if not SPREADSHEET_NAME:
        _initialization_error = "A variável de ambiente 'GOOGLE_SHEETS_NAME' não foi definida."
        return _initialization_error

    try:
        print("INFO: Tentando conectar-se ao Google Sheets...")
        _gc_client = gspread.service_account(filename=SERVICE_ACCOUNT_KEY_PATH)
        sh = _gc_client.open(SPREADSHEET_NAME)
        _worksheet = sh.sheet1
        print("INFO: Conexão com Google Sheets estabelecida com sucesso.")
        return None
    except gspread.exceptions.SpreadsheetNotFound:
        _initialization_error = f"Erro: A planilha '{SPREADSHEET_NAME}' não foi encontrada."
        return _initialization_error
    except Exception as e:
        _initialization_error = f"Erro ao inicializar a conexão com Google Sheets: {e}"
        return _initialization_error

def append_row(data: List[Any]) -> Optional[str]:
    """
    Adiciona uma nova linha à planilha configurada.

    Args:
        data (List[Any]): Uma lista de valores a serem inseridos como uma nova linha.

    Returns:
        Optional[str]: Uma mensagem de erro em caso de falha, ou None se a operação for bem-sucedida.
    """
    # Garante que a conexão esteja ativa antes de tentar escrever
    init_error = _initialize_connection()
    if init_error:
        return f"Serviço indisponível devido a erro de configuração: {init_error}"

    try:
        # A verificação acima garante que _worksheet não é None
        _worksheet.append_row(data) # type: ignore [union-attr]
        return None
    except Exception as e:
        error_message = f"Falha ao escrever na planilha: {e}"
        print(f"ERROR: {error_message}")
        return error_message