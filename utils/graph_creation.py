import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Optional, List

# Definindo as 5 categorias CIF fixas e a ordem desejada
FIXED_ICF_COMPONENT_LABELS: List[str] = [
    'Funções Corporais (b)',
    'Atividades e Participação (d)',
    'Ambiente (e)',
    'Estruturas Corporais (s)',
    'Outros'
]

# Mapeamento fixo de cores para cada categoria
ICF_COMPONENT_COLOR_MAP: Dict[str, str] = {
    'Funções Corporais (b)': '#FFC145',      # Amarelo/Laranja
    'Atividades e Participação (d)': '#B7F242',  # Verde claro
    'Ambiente (e)': '#4369C0',              # Azul
    'Estruturas Corporais (s)': '#DA3B95',    # Rosa/Roxo
    'Outros': '#AAAAAA'                     # Cinza
}

def create_pie_chart(
    input_df: pd.DataFrame,
    title: str = "Distribuição da Classificação"
) -> Optional[go.Figure]:
    """
    Generates a pie chart from a DataFrame, using consistent colors for ICF categories
    present in the input data.

    Args:
        input_df (pd.DataFrame): DataFrame with 'Componente CIF' (labels)
                                 and 'Frequencia' (values) columns.
        title (str): The title of the chart.

    Returns:
        Optional[go.Figure]: The Plotly Figure object containing the pie chart,
                             or None if there is no valid data to plot (e.g., all frequencies are zero or negative).
    """
    # Verificar se o DataFrame de entrada está vazio
    # Check if the input DataFrame is empty
    if input_df.empty:
        print(f"Aviso: DataFrame de entrada para o gráfico de pizza '{title}' está vazio. Retornando None.")
        return None

    # Filtrar categorias com frequência zero ou negativa, pois não aparecem no gráfico de pizza
    # Filter out categories with zero or negative frequency, as they don't appear in a pie chart
    plot_df = input_df[input_df['Frequencia'] > 0].copy()

    # Verificar se há dados válidos para plotar após a filtragem
    # Check if there's any valid data to plot after filtering
    if plot_df.empty:
        print(f"Aviso: Nenhum dado com frequência positiva para gerar o gráfico de pizza: '{title}'. Retornando None.")
        return None

    # Garantir a ordem das categorias no gráfico e na legenda para as categorias presentes
    # Ensure the order of categories in the chart and legend for present categories
    category_order_map = {'Componente CIF': FIXED_ICF_COMPONENT_LABELS}

    figure = px.pie(
        plot_df,
        names='Componente CIF',
        values='Frequencia',
        title=title,
        color='Componente CIF',
        color_discrete_map=ICF_COMPONENT_COLOR_MAP, # Usar o mapeamento fixo de cores
        category_orders=category_order_map          # Forçar a ordem para categorias presentes
    )

    figure.update_layout(legend_title_text='Componentes')
    figure.update_traces(
        direction='clockwise',
        rotation=-30, # Rotação inicial das fatias
        textinfo="label+value+percent",
        textposition='outside',
        textfont_size=16,
        pull=0.05, # Destaca ligeiramente as fatias
        hovertemplate="<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem: %{percent}<extra></extra>"
    )
    return figure

def create_bar_chart(
    input_df: pd.DataFrame,
    title: str = "Frequência da Classificação"
) -> Optional[go.Figure]:
    """
    Generates a bar chart from a DataFrame, using consistent colors for ICF categories
    present in the input data.

    Args:
        input_df (pd.DataFrame): DataFrame with 'Componente CIF' (X-axis)
                                 and 'Frequencia' (Y-axis) columns.
        title (str): The title of the chart.

    Returns:
        Optional[go.Figure]: The Plotly Figure object containing the bar chart,
                             or None if there is no valid data to plot (e.g., all frequencies are zero).
    """
    # Verificar se o DataFrame de entrada está vazio
    # Check if the input DataFrame is empty
    if input_df.empty:
        print(f"Aviso: DataFrame de entrada para o gráfico de barras '{title}' está vazio. Retornando None.")
        return None

    # Verificar se todas as frequências são zero (ou menores)
    # Check if all frequencies are zero (or less)
    # Embora frequências devam ser não-negativas, somar pode ser problemático se houver NaNs.
    # A simple check for non-positive sum is robust if data is clean.
    # If 'Frequencia' can have NaN, they should be handled (e.g., fillna(0) or dropna())
    # For simplicity, assuming 'Frequencia' is numeric and NaNs are not the primary concern here.
    # A more robust check for "no positive data" might be (input_df['Frequencia'] <= 0).all()
    # but sum() == 0 is what was implicitly checked before with merged_df.
    if input_df['Frequencia'].sum() == 0: # Assuming frequencies are non-negative
        print(f"Aviso: Todos os dados em input_df têm frequência 0 para o gráfico de barras: '{title}'. Retornando None.")
        return None

    # Garantir a ordem das categorias no gráfico para as categorias presentes
    # Ensure the order of categories in the chart for present categories
    category_order_map = {'Componente CIF': FIXED_ICF_COMPONENT_LABELS}

    figure = px.bar(
        input_df, # Usar o DataFrame de entrada diretamente
        x='Componente CIF',
        y='Frequencia',
        title=title,
        labels={'Componente CIF': 'Componentes CIF', 'Frequencia': 'Frequência'},
        color='Componente CIF',
        color_discrete_map=ICF_COMPONENT_COLOR_MAP, # Usar o mapeamento fixo de cores
        category_orders=category_order_map,         # Forçar a ordem para categorias presentes
        text_auto=True # Exibe o valor da frequência em cima da barra automaticamente
    )

    figure.update_layout(
        legend_title_text='Componentes',
        xaxis_title="Componentes CIF",
        yaxis_title="Frequência",
        showlegend=True # Garante que a legenda seja mostrada
    )
    figure.update_traces(
        textfont_size=14,
        textangle=0,
        textposition="inside", # Posição do texto da frequência (pode ser 'inside' ou 'outside')
        hovertemplate="<b>%{x}</b><br>Frequência: %{y}<extra></extra>"
    )
    return figure

def create_tree_map_chart(
    tree_map_df: pd.DataFrame,
    title: str = "Treemap de Frequências por Hierarquia de Códigos"
) -> Optional[go.Figure]:
    """
    Generates a Treemap chart from a DataFrame.

    Args:
        tree_map_df (pd.DataFrame): DataFrame with 'Parent', 'Subparent',
                                    'Filho' (Child), and 'Frequencia' (Frequency) columns.
        title (str): The title of the chart.

    Returns:
        Optional[go.Figure]: The Plotly Figure object containing the Treemap chart,
                             or None if the DataFrame is empty.
    """
    if tree_map_df.empty:
        print(f"Aviso: DataFrame vazio para gerar o Treemap: '{title}'.")
        return None

    figure = px.treemap(
        tree_map_df,
        path=['Parent', 'Subparent', 'Filho'], # Define a hierarquia
        values='Frequencia', # Define os valores que determinam o tamanho dos retângulos
        title=title,
        color='Frequencia', # Colore os retângulos com base na frequência
        color_continuous_scale='spectral_r', # Esquema de cores
        height=700, # Altura do gráfico
    )

    figure.update_traces(
        textinfo="label+value+percent entry", # Informações exibidas em cada retângulo
        hovertemplate='<b>%{label}</b><br>Frequência: %{value}<br>Porcentagem: %{percentEntry:.1%}<extra></extra>',
    )

    return figure
