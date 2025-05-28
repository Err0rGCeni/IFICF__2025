import re
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Tuple, Optional, List

def create_pie_graph(dados: Dict[str, int], titulo: str = "Distribuição da Classificação") -> Optional[go.Figure]:
    """
    Gera um gráfico de pizza (pie chart) a partir de um dicionário de atributos e valores.

    Args:
        dados (Dict[str, int]): Um dicionário onde as chaves são os nomes dos atributos
                                 e os valores são os números correspondentes.
        titulo (str): O título do gráfico.

    Returns:
        Optional[go.Figure]: O objeto Figure do Plotly contendo o gráfico de pizza,
                             ou None se não houver dados válidos para plotar.
    """
    dados_validos = {k: v for k, v in dados.items() if v > 0}

    if not dados_validos:
        print(f"Aviso: Nenhum dado com valor > 0 para gerar o gráfico de pizza: '{titulo}'.")
        return None

    labels = list(dados_validos.keys())
    valores = list(dados_validos.values())
    
    colors = ['#FFC145', '#B7F242', '#4369C0', '#DA3B95', '#CCCCCC']

    fig = px.pie(
        names=labels,
        values=valores,
        title=titulo,
        color=labels,
        color_discrete_sequence=colors,
    )

    fig.update_layout(legend_title_text='Componentes')
    fig.update_traces(
        direction='clockwise',
        rotation=-30,
        textinfo="label+value+percent",
        textposition='outside',
        textfont_size=16,
        pull=0.05,
        hovertemplate="<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem: %{percent}<extra></extra>"
    )
    return fig

def create_bar_graph(dados: Dict[str, int], titulo: str = "Frequência da Classificação") -> Optional[go.Figure]:
    """
    Gera um gráfico de barras a partir de um dicionário de atributos e valores.

    Args:
        dados (Dict[str, int]): Um dicionário onde as chaves são os nomes dos atributos
                                 e os valores são os números correspondentes.
        titulo (str): O título do gráfico.

    Returns:
        Optional[go.Figure]: O objeto Figure do Plotly contendo o gráfico de barras,
                             ou None se não houver dados válidos para plotar.
    """
    dados_validos = {k: v for k, v in dados.items() if v > 0}

    if not dados_validos:
        print(f"Aviso: Nenhum dado com valor > 0 para gerar o gráfico de barras: '{titulo}'.")
        return None

    labels = list(dados_validos.keys())
    valores = list(dados_validos.values())

    colors = ['#FFC145', '#B7F242', '#4369C0', '#DA3B95', '#CCCCCC']

    fig = px.bar(
        x=labels,
        y=valores,
        title=titulo,
        labels={'x': 'Componentes CIF', 'y': 'Frequência'},
        color=labels,
        color_discrete_sequence=colors,
        text_auto=True
    )

    fig.update_layout(
        legend_title_text='Componentes',
        xaxis_title="Componentes CIF",
        yaxis_title="Frequência",
        showlegend=True
    )
    fig.update_traces(
        textfont_size=14,
        textangle=0,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Frequência: %{y}<extra></extra>"
    )
    return fig

def create_tree_map_graph(treemap_df: pd.DataFrame, titulo: str = "Treemap de Frequências por Hierarquia de Códigos") -> Optional[go.Figure]:
    fig = px.treemap(
        treemap_df,
        path=['Parent', 'Subparent', 'Filho'], # A hierarquia
        values='Frequencia',
        title=titulo,
        color='Frequencia', # Opcional: colorir por frequência
        color_continuous_scale='Viridis', # Esquema de cores
        height=700
    )

    # Adicionar tooltips úteis (informações ao passar o mouse)
    fig.update_traces(
        textinfo="label+value+percent entry", # Mostra o label, o valor e a porcentagem
        hovertemplate='<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem: %{percentEntry:.1%}<extra></extra>'
    )
    return fig