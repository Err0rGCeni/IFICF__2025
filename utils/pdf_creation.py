import io
import re
import os
import tempfile
import plotly.graph_objects as go
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY # Importe TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

def _handle_text_content(story: list, text: str, styles) -> None:
    """
    Processa e adiciona blocos de texto ao story para o PDF,
    utilizando regex para formatar a "Frase de Entrada" e garantindo negrito.

    Args:
        story (list): A lista de elementos do ReportLab a serem adicionados ao PDF.
        text (str): O texto a ser processado.
        styles: Os estilos de parágrafo do ReportLab.
    """
    # Criar um estilo customizado para a "Frase de Entrada" em negrito
    # Copia o estilo h3 e adiciona o negrito

    h2_bold_style = ParagraphStyle(
        name='H2Bold',
        parent=styles['h2'],
        fontName='Helvetica-Bold', # Garante que a fonte seja negrito
        textColor=colors.darkred,
        alignment=TA_CENTER # Aplica o alinhamento justificado
    )

    h3_bold_style = ParagraphStyle(
        name='H3Bold',
        parent=styles['h3'],
        fontName='Helvetica-Bold' # Garante que a fonte seja negrito
    )

    alert_style = ParagraphStyle(
        name='Alert',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.gray,
        alignment=TA_JUSTIFY # Aplica o alinhamento justificado
    )

    # Criar um estilo customizado para parágrafos normais justificados
    normal_justify_style = ParagraphStyle(
        name='NormalJustify',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY # Aplica o alinhamento justificado
    )

    # Criar um estilo customizado para itens de lista justificados (opcional)
    list_item_justify_style = ParagraphStyle(
        name='ListItemJustify',
        parent=styles['Normal'], # Baseado no estilo normal
        leftIndent=20,           # Indentação para itens de lista
        alignment=TA_JUSTIFY     # Aplica o alinhamento justificado
    )

    story.append(Paragraph(f"Resposta Gerada por IA em {datetime.now().strftime('%d-%m-%Y')}", h2_bold_style))
    story.append(Paragraph(f"IAs podem cometer erros. Quando possível, revise o conteúdo gerado.", alert_style))
    story.append(Spacer(1, 2 * 10))

    blocos = text.split('---')
    
    for bloco in blocos:
      bloco = bloco.strip()
      if not bloco:
          continue

      linhas = [linha.strip() for linha in bloco.split('\n') if linha.strip()]
      if not linhas:
          continue

      primeira_linha = linhas[0]

      match_frase_entrada = re.match(r'^-?\s*(Frase de Entrada:.*)', primeira_linha, re.IGNORECASE)

      if primeira_linha.lower().startswith('resposta fornecida pela llm') or \
          primeira_linha.lower().startswith('okay, sou seu assistente especializado em cif'):
          # Usa o novo estilo justificado para parágrafos normais
          story.append(Paragraph(primeira_linha, normal_justify_style))
      elif match_frase_entrada:
          story.append(Spacer(1, 0.2 * 10))

          conteudo_frase = match_frase_entrada.group(1).strip()
          story.append(Paragraph(conteudo_frase, h3_bold_style))
      else:
          # Usa o novo estilo justificado para parágrafos normais
          story.append(Paragraph(primeira_linha, normal_justify_style))

      for i in range(1, len(linhas)):
          linha = linhas[i]
          if re.match(r'^-?\s*(.*)', linha):
              conteudo_lista_match = re.match(r'^-?\s*(.*)', linha)
              if conteudo_lista_match:
                  conteudo_lista = conteudo_lista_match.group(1).strip()
                  # Usa o estilo justificado para itens de lista
                  story.append(Paragraph(f"• {conteudo_lista}", list_item_justify_style))
              else:
                  # Fallback para texto normal justificado
                  story.append(Paragraph(linha, normal_justify_style))
          else:
              # Usa o novo estilo justificado para parágrafos normais
              story.append(Paragraph(linha, normal_justify_style))
      story.append(Spacer(1, 0.2 * 10))

def _handle_dataframe_content(story: list, dataframes: list[pd.DataFrame], styles) -> None:
    """
    Adiciona DataFrames formatados como tabelas ao story para o PDF.

    Args:
        story (list): A lista de elementos do ReportLab a serem adicionados ao PDF.
        dataframes (list[pd.DataFrame]): Uma lista de DataFrames a serem incluídos.
        styles: Os estilos de parágrafo do ReportLab.
    """
    for i, df in enumerate(dataframes):
        story.append(PageBreak()) # Adiciona quebra de página antes de cada gráfico
        story.append(Paragraph(f"Dados (DataFrame {i+1}):", styles['h2']))
        story.append(Spacer(1, 0.1 * 10))

        data_for_table = [df.columns.tolist()] + df.values.tolist()
        table = Table(data_for_table)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.5 * 10))

def _handle_plotly_plot(story: list, plotly_figs: list[go.Figure], styles) -> None:
    """
    Converte gráficos Plotly em imagens e os adiciona ao story para o PDF.

    Args:
        story (list): A lista de elementos do ReportLab a serem adicionados ao PDF.
        plotly_figs (list[go.Figure]): Uma lista de objetos Plotly Figure a serem incluídos.
        styles: Os estilos de parágrafo do ReportLab.
    """
    for i, fig_plotly in enumerate(plotly_figs):
        try:
            img_buffer = io.BytesIO()
            fig_plotly.write_image(img_buffer, format="png", width=800, height=500, scale=2)
            img_buffer.seek(0)

            img = Image(img_buffer)
            img.drawHeight = 350
            img.drawWidth = 550
            
            story.append(PageBreak()) # Adiciona quebra de página antes de cada gráfico
            story.append(Paragraph(f"Gráfico Gerado ({i+1}):", styles['h2']))
            story.append(Spacer(1, 0.1 * 10))
            story.append(img)
            story.append(Spacer(1, 0.4 * 10))
        except Exception as e:
            story.append(Paragraph(f"Erro ao adicionar gráfico Plotly {i+1}: {e}", styles['Normal']))
            story.append(Spacer(1, 0.2 * 10))

def generate_pdf_report(plotly_figs: list[go.Figure], dataframes: list[pd.DataFrame], text: str, titulo_relatorio: str) -> str:
    """
    Gera um arquivo PDF contendo múltiplos gráficos Plotly, DataFrames e um título,
    segmentando o conteúdo em funções menores.

    Args:
        plotly_figs (list[go.Figure]): Uma lista de objetos Plotly Figure a serem incluídos no PDF.
        dataframes (list[pd.DataFrame]): Uma lista de DataFrames a serem incluídos no PDF.
        text (str): O texto a ser incluído no PDF.
        titulo_relatorio (str): Uma string para ser usada como título/descrição no PDF.

    Returns:
        str: O caminho completo para o arquivo PDF gerado.
    """
    pdf_filename = f"{titulo_relatorio.replace(' ', '_').lower()}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 1. Adicionar o Título do Relatório
    title_style = styles['h1']
    title_style.alignment = TA_CENTER
    story.append(Paragraph(titulo_relatorio, title_style))
    story.append(Spacer(1, 0.8 * 10))

    # 2. Adicionar conteúdo de texto
    _handle_text_content(story, text, styles)

    # 3. Adicionar DataFrames
    if dataframes: # Só adiciona se houver DataFrames na lista
        _handle_dataframe_content(story, dataframes, styles)

    # 4. Adicionar os Gráficos Plotly
    if plotly_figs: # Só adiciona se houver gráficos na lista
        _handle_plotly_plot(story, plotly_figs, styles)

    # 5. Construir o PDF
    try:
        doc.build(story)
        print(f"PDF '{pdf_filename}' gerado com sucesso!")
        return pdf_filename
    except Exception as e:
        print(f"Erro ao gerar o PDF: {e}")
        return ""
    
def generate_pdf_report_temp(plotly_figs: list[go.Figure], dataframes: list[pd.DataFrame], text: str, titulo_relatorio: str) -> str:
    """
    Gera um arquivo PDF temporário para download.
    Args:
        plotly_figs (list[go.Figure]): Uma lista de objetos Plotly Figure a serem incluídos no PDF.
        dataframes (list[pd.DataFrame]): Uma lista de DataFrames a serem incluídos no PDF.
        text (str): O texto a ser incluído no PDF.
        titulo_relatorio (str): Uma string para ser usada como título/descrição no PDF.

    Returns:
        str: O caminho completo para o arquivo PDF gerado.
    """
    pdf_filename = f"{titulo_relatorio.replace(' ', '_').lower()}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 1. Adicionar o Título do Relatório
    title_style = styles['h1']
    title_style.alignment = TA_CENTER
    story.append(Paragraph(titulo_relatorio, title_style))
    story.append(Spacer(1, 0.6 * 10))

    # 2. Adicionar conteúdo de texto
    _handle_text_content(story, text, styles)

    # 3. Adicionar DataFrames
    if dataframes: # Só adiciona se houver DataFrames na lista
        _handle_dataframe_content(story, dataframes, styles)

    # 4. Adicionar os Gráficos Plotly
    if plotly_figs: # Só adiciona se houver gráficos na lista
        _handle_plotly_plot(story, plotly_figs, styles)

    # 5. Construir o PDF
    try:
        doc.build(story)
        print(f"PDF temporário '{pdf_filename}' gerado com sucesso!")
        return pdf_filename
    except Exception as e:
        print(f"Erro ao gerar o PDF: {e}")
        # Se ocorrer um erro, tente remover o arquivo temporário se ele foi criado
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
        return ""