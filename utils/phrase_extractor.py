import fitz  # PyMuPDF: Biblioteca para trabalhar com arquivos PDF
from docx import Document # python-docx: Biblioteca para trabalhar com arquivos DOCX
import os # Módulo para interagir com o sistema operacional (caminhos de arquivo)

def ler_pdf(caminho_pdf: str) -> str:
    """
    Lê o conteúdo textual de um arquivo PDF.

    Esta função abre o arquivo PDF especificado, itera por suas páginas
    e extrai todo o texto contido nelas, concatenando-o em uma única string.

    Args:
        caminho_pdf (str): O caminho completo para o arquivo PDF a ser lido.

    Returns:
        str: Uma string contendo todo o texto extraído do PDF.
             Retorna uma string vazia se ocorrer um erro durante a leitura.
    """
    try:
        doc = fitz.open(caminho_pdf)
        texto_total = ""
        for pagina in doc:
            texto_total += pagina.get_text()
        return texto_total
    except Exception as e:
        print(f"Erro ao ler PDF '{caminho_pdf}': {e}")
        return ""

def ler_docx(caminho_docx: str) -> str:
    """
    Lê o conteúdo textual de um arquivo DOCX (Microsoft Word).

    Esta função abre o arquivo DOCX especificado e extrai o texto
    de todos os parágrafos, concatenando-o em uma única string.

    Args:
        caminho_docx (str): O caminho completo para o arquivo DOCX a ser lido.

    Returns:
        str: Uma string contendo todo o texto extraído do DOCX.
             Retorna uma string vazia se ocorrer um erro durante a leitura.
    """
    try:
        doc = Document(caminho_docx)
        texto_total = ""
        for paragrafo in doc.paragraphs:
            texto_total += paragrafo.text + "\n" # Adiciona nova linha entre parágrafos
        return texto_total
    except Exception as e:
        print(f"Erro ao ler DOCX '{caminho_docx}': {e}")
        return ""

def ler_txt(caminho_txt: str) -> str:
    """
    Lê o conteúdo textual de um arquivo TXT.

    Esta função abre o arquivo de texto especificado e lê todo o seu conteúdo.

    Args:
        caminho_txt (str): O caminho completo para o arquivo TXT a ser lido.

    Returns:
        str: Uma string contendo todo o texto lido do arquivo TXT.
             Retorna uma string vazia se ocorrer um erro durante a leitura.
    """
    try:
        with open(caminho_txt, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except Exception as e:
        print(f"Erro ao ler TXT '{caminho_txt}': {e}")
        return ""

def limpar_e_filtrar_frases(texto: str) -> list[str]:
    """
    Processa um bloco de texto, dividindo-o em linhas, limpando cada linha
    e filtrando frases que são vazias, contêm apenas espaços ou são puramente numéricas.
    Garante que as frases retornadas sejam únicas.

    Args:
        texto (str): O bloco de texto bruto a ser processado.

    Returns:
        list[str]: Uma lista de strings, onde cada string é uma frase limpa e única.
                   A ordem das frases na lista pode não ser a mesma do texto original
                   devido ao uso de um `set` para garantir unicidade.
    """
    if not texto:
        return []

    linhas = texto.split('\n')
    frases_processadas = set() # Usar um set para garantir unicidade automaticamente

    for linha in linhas:
        linha_limpa = linha.strip()
        # Ignora linhas vazias ou que contêm apenas dígitos
        if linha_limpa and not linha_limpa.isdigit():
            frases_processadas.add(linha_limpa)

    return list(frases_processadas) # Converte de volta para lista

def processar_arquivo(caminho_arquivo: str) -> list[str]:
    """
    Função principal que processa um arquivo de entrada (PDF, DOCX ou TXT),
    extrai seu conteúdo textual e, em seguida, limpa e filtra as frases
    encontradas.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo a ser processado.

    Returns:
        list[str]: Uma lista de strings, onde cada string é uma frase limpa e única
                   extraída do arquivo.

    Raises:
        ValueError: Se o formato do arquivo não for suportado (apenas .pdf, .docx, .txt).
    """
    extensao = os.path.splitext(caminho_arquivo)[-1].lower() # Extrai a extensão do arquivo
    texto_bruto = ""

    if extensao == ".pdf":
        texto_bruto = ler_pdf(caminho_arquivo)
    elif extensao in [".doc", ".docx"]: # Suporta ambas as extensões para DOCX
        texto_bruto = ler_docx(caminho_arquivo)
    elif extensao == ".txt":
        texto_bruto = ler_txt(caminho_arquivo)
    else:
        raise ValueError(f"Formato de arquivo não suportado: '{extensao}'. Use PDF, DOCX ou TXT.")

    if not texto_bruto:
        print(f"Atenção: Não foi possível extrair texto do arquivo '{caminho_arquivo}'.")
        return []

    frases = limpar_e_filtrar_frases(texto_bruto)
    return frases

# --- Exemplo de Uso (Mantido para Teste Local) ---
if __name__ == "__main__":
    # Certifique-se de ter um arquivo de teste no mesmo diretório ou ajuste o caminho
    # Exemplo: crie um arquivo 'teste.txt', 'teste.pdf' ou 'teste.docx' na pasta 'sandbox'
    caminho_arquivo_exemplo = "./sandbox/questionariosf-36.txt"
    
    if os.path.exists(caminho_arquivo_exemplo):
        print(f"Tentando processar o arquivo: '{caminho_arquivo_exemplo}'")
        try:
            frases_extraidas = processar_arquivo(caminho_arquivo_exemplo)
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