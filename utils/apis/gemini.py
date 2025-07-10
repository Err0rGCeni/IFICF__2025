# utils/apis/gemini.py
import os
import pathlib

from typing import Optional, Union, List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

from utils.prompts import icf_gemini_prompt

load_dotenv()

# Chave da API e ID do Modelo obtidos do ambiente
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("A variável de ambiente 'GEMINI_API_KEY' não foi definida.")

MODEL_ID = os.getenv('MODEL_ID', 'gemini-2.5-flash')
# --- CAMINHOS E ARQUIVOS DE CONTEXTO ---

# Define o caminho para o prompt do sistema e o PDF de contexto usando pathlib para compatibilidade de SO
BASE_DIR = pathlib.Path(__file__).parent.parent.parent
PDF_CONTEXT_PATH = BASE_DIR / "CIF" / "ListaCIF.pdf"
SYSTEM_PROMPT_PATH = BASE_DIR / "utils" / "prompts.py"

def _load_sys_instruction(caminho: pathlib.Path) -> str:
    """Carrega a string do prompt do sistema a partir de um arquivo Python."""
    try:        
        return icf_gemini_prompt
    except (ImportError, FileNotFoundError):
        print(f"Aviso: Não foi possível encontrar ou importar o prompt do sistema de '{caminho}'. Usando um prompt padrão.")
        return "Você é um especialista na Classificação Internacional de Funcionalidade (CIF). Classifique o texto fornecido de acordo com a CIF e forneça uma análise detalhada."

def _create_file_part(file_path_str: str) -> types.Part:
    """
    Valida, lê e cria um objeto Part a partir de um caminho de arquivo.

    Esta função verifica se o arquivo existe e se sua extensão (.txt ou .pdf) é
    suportada. Em caso afirmativo, lê os bytes do arquivo e retorna um objeto
    `types.Part` com o MIME type correto.

    Args:
        file_path_str: O caminho para o arquivo, recebido como string.

    Returns:
        Um objeto `types.Part` pronto para ser enviado à API Gemini.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado no caminho especificado.
        ValueError: Se a extensão do arquivo não for suportada.
    """
    input_file_path = pathlib.Path(file_path_str)

    if not input_file_path.is_file():
        raise FileNotFoundError(f"O arquivo de entrada do usuário não foi encontrado: {input_file_path}")

    file_extension = input_file_path.suffix.lower()
    
    if file_extension == '.pdf':
        mime_type = 'application/pdf'
    elif file_extension == '.txt':
        mime_type = 'text/plain'
    else:
        raise ValueError(
            f"Tipo de arquivo '{file_extension}' não suportado. "
            "Por favor, envie um arquivo .txt ou .pdf."
        )
    
    return types.Part.from_bytes(
        data=input_file_path.read_bytes(),
        mime_type=mime_type
    )

def api_generate(user_input: Dict[str, Any]) -> str:
    """
    Gera uma análise baseada na CIF a partir de um texto ou arquivo de entrada.

    Utiliza um PDF da CIF como contexto fixo e combina com a entrada do usuário
    (seja um texto direto ou o conteúdo de um arquivo) para gerar uma resposta
    usando a API do Gemini.

    Args:
        input_text: Uma string contendo o texto a ser analisado.
        input_file: O caminho para um arquivo de texto (.txt) cujo conteúdo
                    será analisado.

    Returns:
        A string com a análise gerada pelo modelo.

    Raises:
        ValueError: Se ambos `input_text` e `input_file` forem fornecidos, ou se
                    nenhum dos dois for fornecido.
        FileNotFoundError: Se o arquivo `input_file` ou o PDF de contexto
                           não forem encontrados.
    """
    input_type = user_input.get("type")
    content = user_input.get("content")

    # 1. Validação da Entrada
    if not input_type or not content:
        raise ValueError("Dicionário 'user_input' inválido. Faltando 'type' ou 'content'.")

    # 2. Preparação do Contexto
    if not PDF_CONTEXT_PATH.is_file():
        raise FileNotFoundError(f"Arquivo de contexto PDF não encontrado em: {PDF_CONTEXT_PATH}")

    client = genai.Client(api_key=GEMINI_API_KEY)

    system_instruction = _load_sys_instruction(SYSTEM_PROMPT_PATH)

    llm_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
            ),
        response_mime_type='text/plain',
        seed=1,
        system_instruction=[
            types.Part.from_text(text=system_instruction),
        ],
    )

    user_contents = [
        types.Part.from_bytes(
            data=PDF_CONTEXT_PATH.read_bytes(),
            mime_type='application/pdf'
        )
    ]

    # --- Tratamento type & content ---
    if input_type == "text":
        print(f"Processando via texto: \"{str(content)[:100]}...\"")
        user_contents.append(types.Part.from_text(text=str(content)))
    elif input_type == "file":
        print(f"Processando via arquivo: {content}")
        file_part = _create_file_part(str(content))
        user_contents.append(file_part)
    else:
        raise ValueError(f"Tipo de entrada desconhecido: '{input_type}'")
    
    # 3. Chamada à API Gemini    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_contents,
        config=llm_config
    )
    
    return response.text