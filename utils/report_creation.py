import plotly.graph_objects as go
import pandas as pd # Ainda pode ser necessário para type hints ou manipulações leves
from typing import Tuple # Remover Dict, Optional, List se não forem mais usados diretamente aqui

from .graph_creation import create_pie_chart, create_bar_chart, create_tree_map_chart
from .pdf_creation import generate_pdf_report_temp
from .dataframe_creation import process_report_data

# --- FUNÇÃO: Gera os gráficos a partir dos DataFrames ---
def create_report_plots(df_group: pd.DataFrame, df_individual_treemap: pd.DataFrame) -> Tuple[go.Figure, go.Figure, go.Figure]:
    """
    Cria as figuras Plotly dos gráficos a partir dos DataFrames processados.

    Args:
        df_group (pd.DataFrame): DataFrame de frequência por grupo CIF.
        df_individual_treemap (pd.DataFrame): DataFrame para o treemap de códigos individuais.
                                            (Esperado ter colunas: 'Filho', 'Parent', 'Frequencia')

    Returns:
        Tuple[go.Figure, go.Figure, go.Figure]: Figuras de pizza, barras e treemap.
    """
    print("Gerando gráficos...")
    
    fig_pie = create_pie_chart(df_group, title="Distribuição da Classificação por Componentes CIF")
    fig_bar = create_bar_chart(df_group, title="Frequência da Classificação por Componentes CIF")
    fig_tree_map = create_tree_map_chart(df_individual_treemap, title="Treemap de Frequência por Código CIF")
    
    return fig_pie, fig_bar, fig_tree_map

# --- FUNÇÃO: Gera o PDF a partir de DataFrames e Figuras ---
def generate_report_pdf(llm_res: str, df_group: pd.DataFrame, df_group_describe: pd.DataFrame, 
                        df_individual_treemap: pd.DataFrame, df_treemap_describe: pd.DataFrame,
                        fig_pie: go.Figure, fig_bar: go.Figure, fig_tree_map: go.Figure) -> str:
    """
    Gera o arquivo PDF do relatório com base nos DataFrames e figuras Plotly.
    """
    print("Gerando PDF...")
    temp_file_path = generate_pdf_report_temp(
        plotly_figs_list=[fig_pie, fig_bar, fig_tree_map],
        dataframes_list=[df_group, df_group_describe, df_individual_treemap, df_treemap_describe],
        text_block=llm_res, # A resposta original da LLM pode ser incluída no PDF
        report_title_text="Relatório de Classificação por Componentes CIF"
    )
    return temp_file_path

# --- Função principal de orquestração (exemplo de como poderia ser) ---
def main_report_generation_flow(llm_response_text: str) -> str:
    """
    Orquestra todo o fluxo de geração do relatório:
    1. Processa os dados da LLM para criar DataFrames.
    2. Cria os gráficos a partir dos DataFrames.
    3. Gera o PDF do relatório.
    """
    print("Iniciando o fluxo de geração de relatório...")

    # 1. Processar dados e criar DataFrames
    df_group, df_group_desc, df_tree, df_tree_desc = process_report_data(llm_response_text)

    # 2. Criar gráficos
    fig_pie, fig_bar, fig_tree = create_report_plots(df_group, df_tree)

    # 3. Gerar PDF
    pdf_path = generate_report_pdf(
        llm_res=llm_response_text,
        df_group=df_group,
        df_group_describe=df_group_desc,
        df_individual_treemap=df_tree,
        df_treemap_describe=df_tree_desc,
        fig_pie=fig_pie,
        fig_bar=fig_bar,
        fig_tree_map=fig_tree
    )
    
    print(f"Relatório PDF gerado com sucesso em: {pdf_path}")
    return pdf_path