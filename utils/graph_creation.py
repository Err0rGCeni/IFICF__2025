import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Optional, List

# Definindo as 5 categorias CIF fixas e a ordem desejada
# Defining the 5 fixed ICF categories and the desired order
FIXED_ICF_COMPONENT_LABELS: List[str] = [
    'Funções Corporais (b)',
    'Atividades e Participação (d)',
    'Ambiente (e)',
    'Estruturas Corporais (s)',
    'Outros'
]

# Mapeamento fixo de cores para cada categoria
# Fixed color mapping for each category
ICF_COMPONENT_COLOR_MAP: Dict[str, str] = {
    'Funções Corporais (b)': '#FFC145',  # Amarelo/Laranja
    'Atividades e Participação (d)': '#B7F242', # Verde claro
    'Ambiente (e)': '#4369C0',           # Azul
    'Estruturas Corporais (s)': '#DA3B95', # Rosa/Roxo
    'Outros': '#CCCCCC'                   # Cinza
}

def create_pie_chart(
    input_df: pd.DataFrame,
    title: str = "Distribuição da Classificação"
) -> Optional[go.Figure]:
    """
    Generates a pie chart from a DataFrame, ensuring all 5 fixed ICF
    categories are represented with consistent colors.

    Args:
        input_df (pd.DataFrame): DataFrame with 'Componente CIF' (labels)
                                 and 'Frequencia' (values) columns.
        title (str): The title of the chart.

    Returns:
        Optional[go.Figure]: The Plotly Figure object containing the pie chart,
                             or None if there is no valid data to plot.
    """
    # Criar um DataFrame com todas as categorias fixas e frequência 0
    # Create a DataFrame with all fixed categories and frequency 0
    base_df_with_all_categories = pd.DataFrame({
        'Componente CIF': FIXED_ICF_COMPONENT_LABELS,
        'Frequencia': 0
    })

    # Mesclar o DataFrame de entrada com o DataFrame de categorias completas
    # Isso garante que todas as 5 categorias estejam presentes, preenchendo 0 para as ausentes
    # Merge the input DataFrame with the DataFrame of all categories
    # This ensures all 5 categories are present, filling 0 for missing ones
    merged_df = pd.merge(
        base_df_with_all_categories,
        input_df[['Componente CIF', 'Frequencia']],
        on='Componente CIF',
        how='left',
        suffixes=('_base', '') # Suffix for columns from the left DataFrame if there are overlaps
    )
    # Atualizar a frequência com os valores do df de entrada, onde existirem
    # Update the frequency with values from the input_df where they exist
    merged_df['Frequencia'] = merged_df['Frequencia'].fillna(0)

    # Remover a coluna 'Frequencia_base' se ela foi criada (devido ao sufixo no merge)
    # Remove the 'Frequencia_base' column if it was created (due to the suffix in merge)
    if 'Frequencia_base' in merged_df.columns:
        merged_df = merged_df.drop(columns=['Frequencia_base'])

    # Garantir a ordem das categorias no gráfico e na legenda
    # Ensure the order of categories in the chart and legend
    category_order_map = {'Componente CIF': FIXED_ICF_COMPONENT_LABELS}

    figure = px.pie(
        merged_df,
        names='Componente CIF',
        values='Frequencia',
        title=title,
        color='Componente CIF',
        color_discrete_map=ICF_COMPONENT_COLOR_MAP, # Usar o mapeamento fixo de cores
        category_orders=category_order_map # Forçar a ordem
    )

    # Verificar se há alguma frequência maior que zero para evitar erro ou gráfico vazio
    # Check if there is any frequency greater than zero to avoid errors or an empty chart
    if merged_df['Frequencia'].sum() == 0:
        print(f"Aviso: Todos os dados têm valor 0 para gerar o gráfico de pizza: '{title}'. Retornando None.")
        return None

    figure.update_layout(legend_title_text='Componentes')
    figure.update_traces(
        direction='clockwise',
        rotation=-30,
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
    Generates a bar chart from a DataFrame, ensuring all 5 fixed ICF
    categories are represented with consistent colors.

    Args:
        input_df (pd.DataFrame): DataFrame with 'Componente CIF' (X-axis)
                                 and 'Frequencia' (Y-axis) columns.
        title (str): The title of the chart.

    Returns:
        Optional[go.Figure]: The Plotly Figure object containing the bar chart,
                             or None if there is no valid data to plot.
    """
    # Criar um DataFrame com todas as categorias fixas e frequência 0
    # Create a DataFrame with all fixed categories and frequency 0
    base_df_with_all_categories = pd.DataFrame({
        'Componente CIF': FIXED_ICF_COMPONENT_LABELS,
        'Frequencia': 0
    })

    # Mesclar o DataFrame de entrada com o DataFrame de categorias completas
    # Merge the input DataFrame with the DataFrame of all categories
    merged_df = pd.merge(
        base_df_with_all_categories,
        input_df[['Componente CIF', 'Frequencia']],
        on='Componente CIF',
        how='left',
        suffixes=('_base', '')
    )

    # Atualizar a frequência com os valores do df de entrada, onde existirem
    # Update the frequency with values from the input_df where they exist
    merged_df['Frequencia'] = merged_df['Frequencia'].fillna(0)
    # Remover a coluna 'Frequencia_base' se ela foi criada
    # Remove the 'Frequencia_base' column if it was created
    if 'Frequencia_base' in merged_df.columns:
        merged_df = merged_df.drop(columns=['Frequencia_base'])

    # Garantir a ordem das categorias no gráfico
    # Ensure the order of categories in the chart
    category_order_map = {'Componente CIF': FIXED_ICF_COMPONENT_LABELS}

    figure = px.bar(
        merged_df,
        x='Componente CIF',
        y='Frequencia',
        title=title,
        labels={'Componente CIF': 'Componentes CIF', 'Frequencia': 'Frequência'},
        color='Componente CIF',
        color_discrete_map=ICF_COMPONENT_COLOR_MAP, # Usar o mapeamento fixo de cores
        category_orders=category_order_map, # Forçar a ordem
        text_auto=True # Exibe o valor da frequência em cima da barra automaticamente
    )

    # Verificar se há alguma frequência maior que zero
    # Check if there is any frequency greater than zero
    if merged_df['Frequencia'].sum() == 0:
        print(f"Aviso: Todos os dados têm valor 0 para gerar o gráfico de barras: '{title}'. Retornando None.")
        return None

    figure.update_layout(
        legend_title_text='Componentes',
        xaxis_title="Componentes CIF",
        yaxis_title="Frequência",
        showlegend=True # Garante que a legenda seja mostrada
    )
    figure.update_traces(
        textfont_size=14,
        textangle=0,
        textposition="outside", # Posição do texto da frequência
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
