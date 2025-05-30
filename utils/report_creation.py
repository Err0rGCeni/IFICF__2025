import re
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Tuple, Optional, List
from .graph_creation import create_pie_graph, create_bar_graph, create_tree_map_graph
from .pdf_creation import generate_pdf_report_temp

# Constantes
CIF_COMPONENTS: Dict[str, str] = {
    'b': 'Funções Corporais (b)',
    'd': 'Atividades e Participação (d)',
    'e': 'Ambiente (e)',
    's': 'Estruturas Corporais (s)',
    'Outros': 'Outros' # Para códigos como N.D., N.C., N/A
}

# Padrões para códigos especiais (N.D., N.C., N/A)
SPECIAL_CODE_LITERALS: List[str] = ['N.D.', 'N.C.', 'N/A']
# Regex para encontrar qualquer um dos códigos especiais individualmente
COMBINED_SPECIAL_CODES_REGEX: str = r'(?:N\.D\.|N\.C\.|N\/A)' # Não capturante, para contagem total
# Regex para capturar códigos CIF numéricos (prefixo e número)
CIF_NUMERIC_CODE_REGEX: str = r'([bdes])([0-9]+)'
# Regex para capturar códigos CIF numéricos completos (código inteiro)
CIF_FULL_NUMERIC_CODE_REGEX: str = r'([bdes][0-9]+)'
# Regex para encontrar todas as linhas de Categoria CIF
ALL_CIF_CATEGORY_LINES_REGEX: str = r"Codificação CIF: (.+)"

# --- NOVA FUNÇÃO: Processa a resposta da LLM e retorna os DataFrames ---
def process_report_data(llm_res: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Processa a resposta da LLM para extrair dados e criar os DataFrames do relatório.

    Args:
        llm_res (str): A resposta completa da LLM contendo os dados a serem extraídos.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: Uma tupla contendo:
            - df_group (pd.DataFrame): DataFrame de frequência por grupo CIF.
            - df_group_describe (pd.DataFrame): Descrição estatística de df_group.
            - df_individual_treemap (pd.DataFrame): DataFrame para o treemap de códigos individuais.
            - df_treemap_describe (pd.DataFrame): Descrição estatística de df_individual_treemap.
    """
    print("Processando dados para DataFrames...")
    # MODIFICAÇÃO: Passe llm_res diretamente para as funções de contagem.
    # Elas já contêm a lógica para extrair as linhas "Codificação CIF:"
    data_by_group = _count_group_frequencies(llm_res)
    df_group = pd.DataFrame(list(data_by_group.items()), columns=['Componente CIF', 'Frequencia'])

    data_individual_codes = _count_individual_frequencies(llm_res)
    df_individual_treemap = _create_treemap_dataframe(data_individual_codes)

    translation_map = {
        'count': 'Contagem', 'mean': 'Média', 'std': 'Desvio Padrão',
        'min': 'Mínimo', '25%': '25º Percentil', '50%': 'Mediana (50%)',
        '75%': '75º Percentil', 'max': 'Máximo'
    }

    df_group_describe = df_group.describe().reset_index()
    df_group_describe = df_group_describe.rename(columns={'index': 'Estatística'})
    df_group_describe['Estatística'] = df_group_describe['Estatística'].replace(translation_map)
    
    df_treemap_describe = df_individual_treemap.describe().reset_index() 
    df_treemap_describe = df_treemap_describe.rename(columns={'index': 'Estatística'})
    df_treemap_describe['Estatística'] = df_treemap_describe['Estatística'].replace(translation_map)

    return (df_group, df_group_describe, df_individual_treemap, df_treemap_describe)

# --- NOVA FUNÇÃO: Gera os gráficos a partir dos DataFrames ---
def create_report_plots(df_group: pd.DataFrame, df_individual_treemap: pd.DataFrame) -> Tuple[go.Figure, go.Figure, go.Figure]:
    """
    Cria as figuras Plotly dos gráficos a partir dos DataFrames processados.

    Args:
        df_group (pd.DataFrame): DataFrame de frequência por grupo CIF.
        df_individual_treemap (pd.DataFrame): DataFrame para o treemap de códigos individuais.

    Returns:
        Tuple[go.Figure, go.Figure, go.Figure]: Uma tupla contendo:
            - fig_pie (go.Figure): Figura do gráfico de pizza.
            - fig_bar (go.Figure): Figura do gráfico de barras.
            - fig_tree_map (go.Figure): Figura do gráfico treemap.
    """
    print("Gerando gráficos...")
    # As funções create_pie_graph, create_bar_graph, create_tree_map_graph
    # precisam do dicionário original 'data_by_group' e 'data_individual_codes'
    # ou de uma forma de recriá-los a partir dos DataFrames, ou de aceitar os DataFrames diretamente.
    # Por simplicidade, vou assumir que 'data_by_group' pode ser reconstruído de 'df_group'
    # e 'data_individual_codes' pode ser reconstruído de 'df_individual_treemap'
    
    # Reconstruindo data_by_group do df_group para as funções de criação de gráfico
    data_by_group = dict(zip(df_group['Componente CIF'], df_group['Frequencia']))

    fig_pie = create_pie_graph(df_group, titulo="Distribuição da Classificação por Componentes CIF")
    fig_bar = create_bar_graph(df_group, titulo="Frequência da Classificação por Componentes CIF")
    fig_tree_map = create_tree_map_graph(df_individual_treemap, titulo="Treemap de Frequência por Código CIF")
    
    return (fig_pie, fig_bar, fig_tree_map)

# --- NOVA FUNÇÃO: Gera o PDF a partir de DataFrames e Figuras ---
def generate_report_pdf(llm_res: str, df_group: pd.DataFrame, df_group_describe: pd.DataFrame, 
                        df_individual_treemap: pd.DataFrame, df_treemap_describe: pd.DataFrame,
                        fig_pie: go.Figure, fig_bar: go.Figure, fig_tree_map: go.Figure) -> str:
    """
    Gera o arquivo PDF do relatório com base nos DataFrames e figuras Plotly.

    Args:
        llm_res (str): A resposta original da LLM (para incluir no PDF).
        df_group, df_group_describe, df_individual_treemap, df_treemap_describe (pd.DataFrame): DataFrames do relatório.
        fig_pie, fig_bar, fig_tree_map (go.Figure): Figuras Plotly dos gráficos.

    Returns:
        str: Caminho para o arquivo PDF gerado temporariamente.
    """
    print("Gerando PDF...")
    temp_file = generate_pdf_report_temp(
        plotly_figs=[fig_pie, fig_bar, fig_tree_map],
        dataframes=[df_group, df_group_describe, df_individual_treemap, df_treemap_describe],
        text=llm_res,
        titulo_relatorio="Relatório de Classificação por Componentes CIF"
    )
    return temp_file

def _count_group_frequencies(llm_res: str) -> Dict[str, int]:
    print(llm_res)
    group_frequencies: Dict[str, int] = {label: 0 for label in CIF_COMPONENTS.values()}
    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)    
    if not all_cif_category_lines:
        return group_frequencies
    for cif_category_line in all_cif_category_lines:
        numeric_matches = re.findall(CIF_NUMERIC_CODE_REGEX, cif_category_line)
        for prefix, _ in numeric_matches:
            component_name = CIF_COMPONENTS.get(prefix.lower())
            if component_name and component_name != CIF_COMPONENTS['Outros']:
                group_frequencies[component_name] += 1
        special_code_matches = re.findall(COMBINED_SPECIAL_CODES_REGEX, cif_category_line)
        if special_code_matches:
            group_frequencies[CIF_COMPONENTS['Outros']] += len(special_code_matches)
        print(f"Frequências por grupo atualizadas: {group_frequencies}")
    return group_frequencies

def _count_individual_frequencies(llm_res: str) -> Dict[str, int]:
    individual_frequencies: Dict[str, int] = {}
    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)
    if not all_cif_category_lines:
        return individual_frequencies
    for cif_category_line in all_cif_category_lines:
        numeric_code_matches = re.findall(CIF_FULL_NUMERIC_CODE_REGEX, cif_category_line)
        for code in numeric_code_matches:
            code_lower = code.lower()
            individual_frequencies[code_lower] = individual_frequencies.get(code_lower, 0) + 1
        for special_code_literal in SPECIAL_CODE_LITERALS:
            pattern = re.escape(special_code_literal)
            matches = re.findall(pattern, cif_category_line)
            if matches:
                individual_frequencies[special_code_literal] = \
                    individual_frequencies.get(special_code_literal, 0) + len(matches)
        print(f"Frequências individuais atualizadas: {individual_frequencies}")
    return individual_frequencies

def _create_treemap_dataframe(data_dict: dict) -> pd.DataFrame:
    df = pd.DataFrame(list(data_dict.items()), columns=['Filho', 'Frequencia'])
    parents = []
    subparents = []
    for index, row in df.iterrows():
        code = str(row['Filho'])
        parent = 'Outros'
        subparent = 'Outros'
        if code.startswith('s'):
            parent = 's'
        elif code.startswith('d'):
            parent = 'd'
        elif code.startswith('b'):
            parent = 'b'
        elif code.startswith('e'):
            parent = 'e'
        match = re.match(r'[sdbe]([0-9])', code)
        if match:
            subparent = parent + match.group(1)
        elif parent != 'Outros' and len(code) > 1 and code[1:].isdigit():
            subparent = parent + code[1]
        parents.append(parent)
        subparents.append(subparent)
    df['Parent'] = parents
    df['Subparent'] = subparents
    df_treemap = df.sort_values(by=['Parent', 'Subparent', 'Filho']).reset_index(drop=True)
    return df_treemap