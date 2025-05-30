import fitz  # PyMuPDF: Library for working with PDF files
from docx import Document  # python-docx: Library for working with DOCX files
import os  # Module for interacting with the operating system (file paths)

def _read_pdf_text(pdf_path: str) -> str:
    """
    Reads the textual content from a PDF file.

    This function opens the specified PDF file, iterates through its pages,
    and extracts all text contained within them, concatenating it into a single string.

    Args:
        pdf_path (str): The full path to the PDF file to be read.

    Returns:
        str: A string containing all text extracted from the PDF.
             Returns an empty string if an error occurs during reading.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        full_text = ""
        for page in pdf_document:
            full_text += page.get_text()
        pdf_document.close() # Good practice to close the document
        return full_text
    except Exception as e:
        print(f"Error reading PDF '{pdf_path}': {e}")
        return ""

def _read_docx_text(docx_path: str) -> str:
    """
    Reads the textual content from a DOCX (Microsoft Word) file.

    This function opens the specified DOCX file and extracts the text
    from all paragraphs, concatenating it into a single string.
    A newline character is added after each paragraph's text.

    Args:
        docx_path (str): The full path to the DOCX file to be read.

    Returns:
        str: A string containing all text extracted from the DOCX.
             Returns an empty string if an error occurs during reading.
    """
    try:
        docx_document = Document(docx_path)
        full_text = [] # Use a list for efficient concatenation
        for paragraph in docx_document.paragraphs:
            full_text.append(paragraph.text)
        return "\n".join(full_text) # Join with newlines
    except Exception as e:
        print(f"Error reading DOCX '{docx_path}': {e}")
        return ""

def _read_txt_file(txt_path: str) -> str:
    """
    Reads the textual content from a TXT file.

    This function opens the specified text file and reads its entire content.
    It assumes UTF-8 encoding.

    Args:
        txt_path (str): The full path to the TXT file to be read.

    Returns:
        str: A string containing all text read from the TXT file.
             Returns an empty string if an error occurs during reading.
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as text_file:
            return text_file.read()
    except Exception as e:
        print(f"Error reading TXT '{txt_path}': {e}")
        return ""

def _clean_and_filter_phrases(raw_text: str) -> list[str]:
    """
    Processes a block of text, splitting it into lines, cleaning each line,
    and filtering out phrases that are empty, contain only whitespace, or are purely numeric.
    Ensures that the returned phrases are unique.

    Args:
        raw_text (str): The raw text block to be processed.

    Returns:
        list[str]: A list of strings, where each string is a unique, cleaned phrase.
                   The order of phrases in the list might not be the same as in the
                   original text due to the use of a set for ensuring uniqueness.
    """
    if not raw_text:
        return []

    lines = raw_text.split('\n')
    # Use a set to automatically ensure uniqueness and for efficient addition
    unique_cleaned_phrases = set()

    for line in lines:
        cleaned_line = line.strip()
        # Ignore empty lines or lines that contain only digits
        if cleaned_line and not cleaned_line.isdigit():
            unique_cleaned_phrases.add(cleaned_line)

    return list(unique_cleaned_phrases) # Convert the set back to a list

def process_file_content(file_path: str) -> list[str]:
    """
    Main function that processes an input file (PDF, DOCX, or TXT),
    extracts its textual content, and then cleans and filters the
    phrases found.

    Args:
        file_path (str): The full path to the file to be processed.

    Returns:
        list[str]: A list of strings, where each string is a unique, cleaned phrase
                   extracted from the file. Returns an empty list if no text
                   is extracted or if an error occurs.

    Raises:
        ValueError: If the file format is not supported (only .pdf, .docx, .doc, .txt).
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower() # Normalize to lowercase

    raw_text_content = ""

    if file_extension == ".pdf":
        raw_text_content = _read_pdf_text(file_path)
    elif file_extension in [".doc", ".docx"]: # Support both .doc and .docx
        raw_text_content = _read_docx_text(file_path)
    elif file_extension == ".txt":
        raw_text_content = _read_txt_file(file_path)
    else:
        raise ValueError(
            f"Formato não suportado: '{file_extension}'. Utilizar PDF, DOCX, or TXT."
        )

    if not raw_text_content:
        print(f"Alerta: Não foi possível realizar a extração:  '{file_path}'.")
        return []

    cleaned_phrases = _clean_and_filter_phrases(raw_text_content)
    return cleaned_phrases

# --- Exemplo de Uso (Mantido para Teste Local) ---
if __name__ == "__main__":
    # Certifique-se de ter um arquivo de teste no mesmo diretório ou ajuste o caminho
    # Exemplo: crie um arquivo 'teste.txt', 'teste.pdf' ou 'teste.docx' na pasta 'sandbox'
    caminho_arquivo_exemplo = "./sandbox/questionariosf-36.txt"
    
    if os.path.exists(caminho_arquivo_exemplo):
        print(f"Tentando processar o arquivo: '{caminho_arquivo_exemplo}'")
        try:
            frases_extraidas = process_file_content(caminho_arquivo_exemplo)
            print(f"\nTipo do resultado: {type(frases_extraidas)}")
            print(f"Frases extraídas de '{caminho_arquivo_exemplo}' ({len(frases_extraidas)}):\n")
            
            if frases_extraidas:
                for i, frase in enumerate(frases_extraidas):
                    print(f"{i+1}. {frase}")
            else:
                print("Nenhuma frase foi extraída do arquivo.")
        except ValueError as ve:
            print(f"Erro: {ve}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
    else:
        print(f"Arquivo de exemplo '{caminho_arquivo_exemplo}' não encontrado.")
        print("Por favor, crie um arquivo para testar ou ajuste o caminho.")