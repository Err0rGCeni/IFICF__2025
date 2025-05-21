import re
import sys

def format_paragraph(paragraph):
    """Formata um parágrafo de acordo com as regras ajustadas."""
    paragraph = paragraph.strip()
    if re.match(r'^[a-z]\d{3}\s', paragraph):
        return "Código: " + re.sub(r'^([a-z]\d{3})\s', r'\1: ', paragraph)
    elif re.match(r'^[a-z]\d{4,}\s', paragraph):
        return "Subcódigo: " + re.sub(r'^([a-z]\d{4,})\s', r'\1: ', paragraph)
    elif paragraph.startswith("Inclui: "):
        return paragraph
    elif not re.match(r'^[a-z]\d+', paragraph):
        return "Descrição: " + paragraph
    return paragraph  # Caso padrão (não deve ocorrer com as regras)

def process_file(input_file, output_file):
    """Lê o arquivo de entrada, formata os parágrafos e grava no arquivo de saída."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return

    # Divide em parágrafos (considerando linhas em branco como separadores)
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    formatted_paragraphs = []

    for i, para in enumerate(paragraphs):
        formatted = format_paragraph(para)
        # Adiciona linha em branco antes de "Código: ", exceto no primeiro parágrafo
        if formatted.startswith("Código: ") and i > 0:
            formatted_paragraphs.append("")
        formatted_paragraphs.append(formatted)

    # Junta os parágrafos com uma única quebra de linha
    output_content = '\n'.join(formatted_paragraphs)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    print(f"Arquivo formatado salvo como '{output_file}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python 0PY_format.py b2.txt")
    else:
        input_file = sys.argv[1]
        output_file = input_file.replace('.txt', '_formatado.txt')
        process_file(input_file, output_file)
        