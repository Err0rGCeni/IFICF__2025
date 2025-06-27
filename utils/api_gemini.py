# utils/api_gemini.py
import os
import pathlib

from typing import Optional, Union, List
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
BASE_DIR = pathlib.Path(__file__).parent.parent
PDF_CONTEXT_PATH = BASE_DIR / "CIF" / "ListaCIF.pdf"
SYSTEM_PROMPT_PATH = BASE_DIR / "utils" / "prompts.py"

def _load_sys_instruction(caminho: pathlib.Path) -> str:
    """Carrega a string do prompt do sistema a partir de um arquivo Python."""
    try:        
        return icf_gemini_prompt
    except (ImportError, FileNotFoundError):
        print(f"Aviso: Não foi possível encontrar ou importar o prompt do sistema de '{caminho}'. Usando um prompt padrão.")
        return "Você é um especialista na Classificação Internacional de Funcionalidade (CIF). Classifique o texto fornecido de acordo com a CIF e forneça uma análise detalhada."

def api_generate(
    input_text: Optional[str] = None,
    input_file: Optional[Union[str, pathlib.Path]] = None,
) -> str:
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
    
    # 1. Validação da entrada (garante que ou texto ou arquivo foi fornecido, mas não ambos)
    if not (input_text is None) ^ (input_file is None):
        raise ValueError("Forneça exatamente um dos parâmetros: 'input_text' ou 'input_file'.")

    # 2. Preparação do Conteúdo (Contents)
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

    # Se a entrada for texto, adiciona um 'Part' de texto.
    if input_text:        
        user_contents.append(
            types.Part.from_text(
                text=input_text,
            )
        )
    
    # Adiciona o arquivo do usuário como um 'Part' de PDF, enviando seus bytes.
    if input_file:
        input_file_path = pathlib.Path(input_file)
        user_contents.append(
            types.Part.from_bytes(
                data=input_file_path.read_bytes(),
                mime_type='application/pdf'
            )
        )
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_contents,
        config=llm_config
    )
    
    return response.text