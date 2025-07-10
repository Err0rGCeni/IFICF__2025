# utils/report/graph_creation.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Tuple # Dict e List não são mais necessários para as constantes globais

# Importa a Enum para centralizar as definições de categoria, rótulos e cores
from .icf_categories import ICFComponent

# Obtém as informações de ordenação e cores diretamente da Enum ICFComponent
ORDERED_ICF_LABELS = ICFComponent.get_ordered_labels()
ICF_COLOR_MAP_FROM_LABEL = ICFComponent.get_color_map() # Mapeia Rótulo Completo -> Cor
ICF_COLOR_MAP_FROM_SHORT_CODE = { # Mapeia Código Curto -> Cor (para o Treemap)
    member.short_code: member.color for member in ICFComponent
}

def create_pie_chart(
    input_df: pd.DataFrame,
    title: str = "Distribuição da Classificação"
) -> Optional[go.Figure]:
    """
    Gera um gráfico de pizza a partir de um DataFrame, usando cores consistentes
    para as categorias CIF presentes nos dados de entrada.

    Args:
        input_df (pd.DataFrame): DataFrame com colunas 'Componente CIF' (rótulos)
                                 e 'Frequencia' (valores).
                                 Espera-se que 'Componente CIF' já esteja como
                                 pd.Categorical ordenado.
        title (str): O título do gráfico.

    Returns:
        Optional[go.Figure]: Objeto Plotly Figure ou None se não houver dados válidos.
    """
    if input_df.empty:
        print(f"Aviso: DataFrame de entrada para o gráfico de pizza '{title}' está vazio. Retornando None.")
        return None

    plot_df = input_df[input_df['Frequência'] > 0].copy()

    if plot_df.empty:
        print(f"Aviso: Nenhum dado com frequência positiva para gerar o gráfico de pizza: '{title}'. Retornando None.")
        return None

    category_order_map = {'Componente CIF': ORDERED_ICF_LABELS}

    figure = px.pie(
        plot_df,
        names='Componente CIF',
        # values='Frequencia', # ANTES
        values='Frequência', # DEPOIS
        title=title,
        color='Componente CIF',
        color_discrete_map=ICF_COLOR_MAP_FROM_LABEL,
        category_orders=category_order_map
    )

    figure.update_layout(legend_title_text='Componentes')
    figure.update_traces(
        direction='clockwise',
        rotation=-30,
        textinfo="label+value+percent",
        textposition='outside',
        textfont_size=16,
        pull=[0.05 if val > 0 else 0 for val in plot_df['Frequência']], # DEPOIS
        hovertemplate="<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem: %{percent}<extra></extra>"
    )
    return figure

def create_bar_chart(
    input_df: pd.DataFrame,
    title: str = "Frequência da Classificação"
) -> Optional[go.Figure]:
    """
    Gera um gráfico de barras a partir de um DataFrame, usando cores consistentes
    para as categorias CIF.

    Args:
        input_df (pd.DataFrame): DataFrame com colunas 'Componente CIF' (eixo X)
                                 e 'Frequencia' (eixo Y).
                                 Espera-se que 'Componente CIF' já esteja como
                                 pd.Categorical ordenado.
        title (str): O título do gráfico.

    Returns:
        Optional[go.Figure]: Objeto Plotly Figure ou None se não houver dados válidos.
    """
    if input_df.empty:
        print(f"Aviso: DataFrame de entrada para o gráfico de barras '{title}' está vazio. Retornando None.")
        return None

    # Para gráficos de barra, podemos plotar frequências zero, então não filtramos > 0
    if not input_df['Frequência'].any(): # DEPOIS
         print(f"Aviso: Todos os dados em input_df têm frequência 0 para o gráfico de barras: '{title}'.")

    category_order_map = {'Componente CIF': ORDERED_ICF_LABELS}

    figure = px.bar(
        input_df,
        x='Componente CIF',
        y='Frequência', # DEPOIS
        title=title,
        labels={'Componente CIF': 'Componentes CIF', 'Frequência': 'Frequência'}, # DEPOIS (chave 'Frequência')
        color='Componente CIF',
        color_discrete_map=ICF_COLOR_MAP_FROM_LABEL,
        category_orders=category_order_map,
        text_auto=True
    )
    figure.update_layout(
        legend_title_text='Componentes',
        xaxis_title="Componentes CIF",
        yaxis_title="Frequência",
        showlegend=True
    )
    figure.update_traces(
        textfont_size=14,
        textangle=0,
        textposition="inside",
        hovertemplate="<b>%{x}</b><br>Frequência: %{y}<extra></extra>"
    )
    return figure

def create_tree_map_chart(
    tree_map_df: pd.DataFrame,
    title: str = "Treemap de Frequências por Hierarquia de Códigos"
) -> Optional[go.Figure]:
    """
    Gera um gráfico Treemap a partir de um DataFrame hierárquico.
    As cores do nível 'Parent' são baseadas nos códigos curtos dos componentes CIF.

    Args:
        tree_map_df (pd.DataFrame): DataFrame com colunas 'Parent', 'Subparent',
                                    'Filho' (Rótulo), e 'Frequencia'.
        title (str): O título do gráfico.

    Returns:
        Optional[go.Figure]: Objeto Plotly Figure ou None se o DataFrame estiver vazio.
    """
    if tree_map_df.empty:
        print(f"Aviso: DataFrame vazio para gerar o Treemap: '{title}'.")
        return None

    # Filtra linhas onde 'Filho' é nulo ou vazio, pois podem causar problemas no treemap
    # e geralmente representam nós estruturais que não devem ser folhas.
    plot_df = tree_map_df.dropna(subset=['Código'])
    plot_df = plot_df[plot_df['Código'] != ""]

    if plot_df.empty:
        print(f"Aviso: DataFrame para Treemap não contém 'Códigos' válidos após filtragem: '{title}'.") # DEPOIS
        return None

    figure = px.treemap(
        plot_df,
        path=['Componente', 'Capítulo', 'Código'],
        values='Frequência',
        title=title,
        color='Componente',
        color_discrete_map=ICF_COLOR_MAP_FROM_SHORT_CODE,
        height=700
    )

    figure.update_traces(
        textinfo="label+value+percent entry", # Informações exibidas
        # Para hovertemplate, %{customdata} pode ser usado se você adicionar colunas extras
        # Exemplo: customdata=plot_df[['Parent', 'Subparent']]
        # hovertemplate='<b>%{label}</b> (%{customdata[0]} > %{customdata[1]})<br>Frequência: %{value}<br>Porcentagem da Entrada: %{percentEntry:.1%}<extra></extra>',
        hovertemplate='<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem da Entrada: %{percentEntry:.1%}<extra></extra>',
        marker_line_width=1,
        marker_line_color='white' # Linhas brancas para separar os blocos
    )
    
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        )
    )
    return figure

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