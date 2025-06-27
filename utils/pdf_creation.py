# utils/pdf_creation.py
import io
import re
import os
import tempfile
import plotly.graph_objects as go
import pandas as pd

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

_STRINGS = {
    "TXT_TIMESTAMP": lambda date: f"Resposta Gerada com IA em {date}",
    "TXT_DISCLAIMER": "IAs podem cometer erros. Revise o conteúdo gerado.",
}

# --- Regex Patterns ---
# Regex para identificar e tratar (o acento pode ser problemático para llms as vezes) 'Frase de Extraída: ...'.

_INPUT_PHRASE_REGEX = re.compile(r'^-?\s*(Frase Extra.*:.*)', re.IGNORECASE)

# Regex para tratar itens de lista.
# Captura caracteres válidos.
_LIST_ITEM_CONTENT_REGEX = re.compile(r'^-?\s*(.*)')

# --- Constants for Text Styling ---
_LLM_RESPONSE_STARTERS = (
    'Resposta Fornecida pela LLM',
)

def _handle_text_content(story: list, text_content: str, styles: dict) -> None:
    """
    Processes and adds text blocks to the PDF story.

    This function formats text, applying specific styles for headers,
    input phrases, and list items. It uses regular expressions to identify
    and format "Input Phrase:" lines, ensuring they are bold.
    It also adds a timestamped AI generation notice and a disclaimer.

    Args:
        story (list): The list of ReportLab Platypus elements to be added to the PDF.
        text_content (str): The raw text string to be processed and formatted.
        styles (dict): A dictionary of ReportLab sample paragraph styles.
    """

    # --- Estilização Customizada ---
    h2_bold_centered_style = ParagraphStyle(
        name='H2BoldCentered',
        parent=styles['h2'],
        fontName='Helvetica-Bold',
        textColor=colors.darkred,
        alignment=TA_CENTER
    )

    h3_bold_style = ParagraphStyle(
        name='H3Bold',
        parent=styles['h3'],
        fontName='Helvetica-Bold'
    )

    alert_message_style = ParagraphStyle(
        name='AlertMessage',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.gray,
        alignment=TA_JUSTIFY
    )

    normal_justified_style = ParagraphStyle(
        name='NormalJustified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY
    )

    list_item_justified_style = ParagraphStyle(
        name='ListItemJustified',
        parent=styles['Normal'],
        leftIndent=20,
        alignment=TA_JUSTIFY
    )

    # Timestamp & Disclaimer (gerado uma vez no início do conteúdo textual)
    # if not story: # Adiciona apenas se a story estiver vazia, para não repetir a cada chamada se a função for reutilizada
    generation_timestamp_text = _STRINGS['TXT_TIMESTAMP'](datetime.now().strftime('%d-%m-%Y'))
    story.append(Paragraph(generation_timestamp_text, h2_bold_centered_style))

    disclaimer_text = _STRINGS['TXT_DISCLAIMER']
    story.append(Paragraph(disclaimer_text, alert_message_style))
    story.append(Spacer(1, 20))

    # Processamento do conteúdo principal
    text_blocks = text_content.split('---')

    for block_content_full in text_blocks: # Renomeado para evitar conflito com 'block' do ReportLab
        current_block_text = block_content_full.strip()
        if not current_block_text:
            continue

        lines_in_block = [line.strip() for line in current_block_text.split('\n') if line.strip()]
        if not lines_in_block:
            continue

        # Processa a primeira linha do bloco atual
        first_line_in_block = lines_in_block[0]
        input_phrase_match_first = _INPUT_PHRASE_REGEX.match(first_line_in_block)

        if any(first_line_in_block.lower().startswith(starter) for starter in _LLM_RESPONSE_STARTERS):
            story.append(Paragraph(first_line_in_block, normal_justified_style))
        elif input_phrase_match_first:
            story.append(Spacer(1, 2))
            input_phrase_text = input_phrase_match_first.group(1).strip()
            story.append(Paragraph(input_phrase_text, h3_bold_style))
        else:
            story.append(Paragraph(first_line_in_block, normal_justified_style))

        # Processa as linhas subsequentes do bloco atual (SE HOUVER)
        if len(lines_in_block) > 1:
            for i in range(1, len(lines_in_block)):
                line_text = lines_in_block[i]
                
                # VERIFICAR "Frase de Entrada" PRIMEIRO para linhas subsequentes
                input_phrase_match_subsequent = _INPUT_PHRASE_REGEX.match(line_text)

                if input_phrase_match_subsequent:
                    story.append(Spacer(1, 2))
                    input_phrase_text_subsequent = input_phrase_match_subsequent.group(1).strip()
                    story.append(Paragraph(input_phrase_text_subsequent, h3_bold_style))
                else:
                    # Se não for "Frase de Entrada", então processe como item de lista ou texto normal
                    list_item_match = _LIST_ITEM_CONTENT_REGEX.match(line_text)
                    
                    if list_item_match:
                        list_item_content = list_item_match.group(1).strip()
                        if list_item_content:
                            story.append(Paragraph(f"• {list_item_content}", list_item_justified_style))
                        # else: (opcional) tratar o caso de list_item_content ser vazio após o strip
                    else:
                        # Com o _LIST_ITEM_CONTENT_REGEX atual, este 'else' é raramente atingido
                        story.append(Paragraph(line_text, normal_justified_style))
            
        story.append(Spacer(1, 12)) # Espaçador após cada bloco de conteúdo (ajuste o valor do spacer conforme necessário)


def _handle_dataframe_content(story: list, dataframes_list: list[pd.DataFrame], styles: dict) -> None:
    """Adiciona DataFrames ao PDF, usando um dicionário interno para títulos descritivos."""
    
    # Dicionário que mapeia o índice do DataFrame ao seu título específico.
    DATAFRAME_TITLES = {
        0: "Tabela de Frequência por Componente CIF",
        1: "Estatísticas Descritivas dos Componentes",
        2: "Tabela de Frequência por Código CIF Específico",
        3: "Estatísticas Descritivas dos Códigos CIF"
    }

    for df_index, df in enumerate(dataframes_list):
        # Usa o título do dicionário se o índice existir; senão, usa um título genérico.
        title = DATAFRAME_TITLES.get(df_index, f"Data (DataFrame {df_index + 1})")
        
        story.append(PageBreak())
        story.append(Paragraph(title, styles['h2']))
        story.append(Spacer(1, 1))

        # O restante da lógica para criar a tabela permanece o mesmo.
        table_data = [df.columns.tolist()] + df.values.tolist()
        pdf_table = Table(table_data)

        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(pdf_table)
        story.append(Spacer(1, 5))


def _handle_plotly_plot(story: list, plotly_figures: list[go.Figure], styles: dict) -> None:
    """Converte e adiciona gráficos Plotly, usando dicionários internos para títulos e configurações."""

    # Dicionário que mapeia o índice do gráfico ao seu título.
    PLOT_TITLES = {
        0: "Distribuição Percentual por Componente",
        1: "Gráfico de Frequência por Componente CIF",
        2: "Análise Hierárquica de Códigos CIF (Treemap)"
    }
    
    # Dicionário que mapeia o índice do gráfico a uma configuração especial.
    PLOT_CONFIGS = {
        2: {'type': 'treemap'}  # O gráfico de índice 2 é um treemap
    }

    for fig_index, plotly_figure in enumerate(plotly_figures):
        try:
            # Pega o título do dicionário, com fallback para o genérico.
            title = PLOT_TITLES.get(fig_index, f"Generated Plot ({fig_index + 1})")
            
            # Pega a configuração do dicionário.
            config = PLOT_CONFIGS.get(fig_index, {})
            plot_type = config.get('type', 'default')

            image_buffer = io.BytesIO()

            # Determina as dimensões com base no 'type' obtido da configuração.
            if plot_type == 'treemap':
                export_height = 800 # _PLOT_IMAGE_SPECIAL_HEIGHT_EXPORT
                draw_height = 550 # _PLOT_IMAGE_SPECIAL_DRAW_HEIGHT
            else:
                export_height = 500 # _PLOT_IMAGE_DEFAULT_HEIGHT_EXPORT
                draw_height = 350 # _PLOT_IMAGE_DEFAULT_DRAW_HEIGHT

            plotly_figure.write_image(
                image_buffer, format="png", width=800, # _PLOT_IMAGE_COMMON_WIDTH_EXPORT
                height=export_height, scale=2 # _PLOT_IMAGE_SCALE
            )
            image_buffer.seek(0)

            reportlab_image = Image(image_buffer)
            reportlab_image.drawHeight = draw_height
            reportlab_image.drawWidth = 550 # _PLOT_IMAGE_COMMON_DRAW_WIDTH

            story.append(PageBreak())
            story.append(Paragraph(title, styles['h2']))
            story.append(Spacer(1, 1))
            story.append(reportlab_image)
            story.append(Spacer(1, 4))

        except Exception as e:
            error_message = f"Error adding Plotly plot '{title}': {e}"
            story.append(Paragraph(error_message, styles['Normal']))
            story.append(Spacer(1, 2))


def generate_pdf_report_temp(
    plotly_figs_list: list[go.Figure],
    dataframes_list: list[pd.DataFrame],
    text_block: str,
    report_title_text: str
) -> str:
    """
    Generates a PDF report and saves it as a temporary file.

    The report includes a title, processed text content, DataFrames as tables,
    and Plotly figures as images.

    Args:
        plotly_figs_list (list[go.Figure]): A list of Plotly Figure objects.
        dataframes_list (list[pd.DataFrame]): A list of pandas DataFrames.
        text_block (str): A string containing the text content to be included.
        report_title_text (str): The title for the PDF report.

    Returns:
        str: The full path to the generated temporary PDF file.
             Returns an empty string if PDF generation fails.
    """
    pdf_filepath = ""
    # Create a temporary file; it won't be deleted automatically (delete=False).
    # This is useful if an external process (like Gradio serving the file) needs it.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdf_filepath = temp_pdf.name

    document = SimpleDocTemplate(pdf_filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story_elements = [] # List to hold all PDF elements

    # 1. Report Title
    title_style = styles['h1']
    title_style.alignment = TA_CENTER # Center align the main title
    story_elements.append(Paragraph(report_title_text, title_style))
    story_elements.append(Spacer(1, 6)) # Spacer after title

    # 2. Processed Text Content
    if text_block and text_block.strip():
        _handle_text_content(story_elements, text_block, styles)

    # 3. DataFrames as Tables
    if dataframes_list: # Only add if there are DataFrames
        _handle_dataframe_content(story_elements, dataframes_list, styles)

    # 4. Plotly Figures as Images
    if plotly_figs_list: # Only add if there are Plotly figures
        _handle_plotly_plot(story_elements, plotly_figs_list, styles)

    # 5. Build the PDF
    try:
        document.build(story_elements)
        print(f"Temporary PDF report '{pdf_filepath}' generated successfully!")
        return pdf_filepath
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        # Attempt to remove the temporary file if an error occurred during PDF build
        if os.path.exists(pdf_filepath):
            try:
                os.remove(pdf_filepath)
                print(f"Cleaned up temporary file '{pdf_filepath}' due to error.")
            except OSError as ose:
                print(f"Error removing temporary file '{pdf_filepath}': {ose}")
        return ""