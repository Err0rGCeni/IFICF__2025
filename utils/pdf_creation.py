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

# --- Pre-compiled Regex Patterns ---
# Regex para identificar e tratar 'Frase de Entrada: ...'.
_INPUT_PHRASE_REGEX = re.compile(r'^-?\s*(Frase de Entrada:.*)', re.IGNORECASE)

# Regex para tratar itens de lista.
# Captura caracteres válidos.
_LIST_ITEM_CONTENT_REGEX = re.compile(r'^-?\s*(.*)')

# --- Constantes para lidar com Plotlys ---
_PLOT_IMAGE_COMMON_WIDTH_EXPORT = 800
_PLOT_IMAGE_DEFAULT_HEIGHT_EXPORT = 500
_PLOT_IMAGE_SPECIAL_HEIGHT_EXPORT = 800  # TreeMap
_PLOT_IMAGE_SCALE = 2

_PLOT_IMAGE_COMMON_DRAW_WIDTH = 550
_PLOT_IMAGE_DEFAULT_DRAW_HEIGHT = 350
_PLOT_IMAGE_SPECIAL_DRAW_HEIGHT = 550  # TreeMap

_SPECIAL_PLOT_INDEX = 2 # TreeMap

# --- Constants for Text Styling ---
_LLM_RESPONSE_STARTERS = (
    'resposta fornecida pela llm',
    'okay, sou seu assistente especializado em cif'
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

    # Timestamp & Disclaimer
    generation_timestamp_text = _STRINGS['TXT_TIMESTAMP'](datetime.now().strftime('%d-%m-%Y'))
    story.append(Paragraph(generation_timestamp_text, h2_bold_centered_style))

    disclaimer_text = _STRINGS['TXT_DISCLAIMER']
    story.append(Paragraph(disclaimer_text, alert_message_style))
    story.append(Spacer(1, 20)) # Standard spacer after disclaimer

    # Processamento do conteúdo principal
    text_blocks = text_content.split('---')

    for block in text_blocks:
        block = block.strip()
        if not block:
            continue

        lines_in_block = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines_in_block:
            continue

        first_line_in_block = lines_in_block[0]
        input_phrase_match = _INPUT_PHRASE_REGEX.match(first_line_in_block)

        if any(first_line_in_block.lower().startswith(starter) for starter in _LLM_RESPONSE_STARTERS):
            story.append(Paragraph(first_line_in_block, normal_justified_style))
        elif input_phrase_match:
            story.append(Spacer(1, 2))
            input_phrase_text = input_phrase_match.group(1).strip()
            story.append(Paragraph(input_phrase_text, h3_bold_style))
        else:
            story.append(Paragraph(first_line_in_block, normal_justified_style))

        # Process subsequent lines in the block
        for i in range(1, len(lines_in_block)):
            line_text = lines_in_block[i]
            list_item_match = _LIST_ITEM_CONTENT_REGEX.match(line_text)

            if list_item_match:
                # group(1) captura o conteúdo após hífen e espaços.
                list_item_content = list_item_match.group(1).strip()
                story.append(Paragraph(f"• {list_item_content}", list_item_justified_style))
            else:                
                story.append(Paragraph(line_text, normal_justified_style))
        story.append(Spacer(1, 2)) # Separador de blocos


def _handle_dataframe_content(story: list, dataframes_list: list[pd.DataFrame], styles: dict) -> None:
    """
    Adds pandas DataFrames to the PDF story, formatted as tables.

    Each DataFrame is preceded by a page break and a title.
    Table styling includes a header row with a grey background and white text,
    and a beige background for data rows, with a grid.

    Args:
        story (list): The list of ReportLab Platypus elements.
        dataframes_list (list[pd.DataFrame]): A list of pandas DataFrames to include.
        styles (dict): A dictionary of ReportLab sample paragraph styles.
    """
    for df_index, df in enumerate(dataframes_list):
        story.append(PageBreak())
        story.append(Paragraph(f"Data (DataFrame {df_index + 1}):", styles['h2']))
        story.append(Spacer(1, 1))

        # Preparação do dataframe para tabela
        table_data = [df.columns.tolist()] + df.values.tolist()
        pdf_table = Table(table_data)

        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),      # Header row background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header row text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # Center alignment for all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),   # Header row font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),            # Header row bottom padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),    # Data rows background
            ('GRID', (0, 0), (-1, -1), 1, colors.black)        # Grid for the entire table
        ]))

        story.append(pdf_table)
        story.append(Spacer(1, 5))


def _handle_plotly_plot(story: list, plotly_figures: list[go.Figure], styles: dict) -> None:
    """
    Converts Plotly figures to PNG images and adds them to the PDF story.

    Each plot is preceded by a page break and a title.
    Handles potential errors during image conversion.
    The third plot (index 2) has specific dimensions.

    Args:
        story (list): The list of ReportLab Platypus elements.
        plotly_figures (list[go.Figure]): A list of Plotly Figure objects.
        styles (dict): A dictionary of ReportLab sample paragraph styles.
    """
    for fig_index, plotly_figure in enumerate(plotly_figures):
        try:
            image_buffer = io.BytesIO()

            # Determine export and draw dimensions based on plot index
            if fig_index == _SPECIAL_PLOT_INDEX:
                export_height = _PLOT_IMAGE_SPECIAL_HEIGHT_EXPORT
                draw_height = _PLOT_IMAGE_SPECIAL_DRAW_HEIGHT
            else:
                export_height = _PLOT_IMAGE_DEFAULT_HEIGHT_EXPORT
                draw_height = _PLOT_IMAGE_DEFAULT_DRAW_HEIGHT

            plotly_figure.write_image(
                image_buffer,
                format="png",
                width=_PLOT_IMAGE_COMMON_WIDTH_EXPORT,
                height=export_height,
                scale=_PLOT_IMAGE_SCALE
            )
            image_buffer.seek(0)

            reportlab_image = Image(image_buffer)
            reportlab_image.drawHeight = draw_height
            reportlab_image.drawWidth = _PLOT_IMAGE_COMMON_DRAW_WIDTH

            story.append(PageBreak())
            story.append(Paragraph(f"Generated Plot ({fig_index + 1}):", styles['h2']))
            story.append(Spacer(1, 1))
            story.append(reportlab_image)
            story.append(Spacer(1, 4))

        except Exception as e:
            error_message = f"Error adding Plotly plot {fig_index + 1}: {e}"
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