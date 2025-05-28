import re
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Tuple, Optional, List
from .graph_creation import create_pie_graph, create_bar_graph, create_tree_map_graph
from .pdf_creation import generate_pdf_report, generate_pdf_report_temp

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
ALL_CIF_CATEGORY_LINES_REGEX: str = r"Categoria CIF: (.+)"

def generate_report(llm_res: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[go.Figure], Optional[go.Figure], Optional[go.Figure], Optional[str], Optional[str]]:
    """
    Gera um relatório a partir da resposta da LLM, extraindo dados de múltiplas
    seções de "Categoria CIF" e criando um gráfico de pizza e um gráfico de barras.

    Args:
        llm_res (str): A resposta completa da LLM contendo os dados a serem extraídos.

    Returns:
        Tuple[Optional[go.Figure], Optional[go.Figure]]: Uma tupla contendo
        a figura do gráfico de pizza e a figura do gráfico de barras.
        Retorna None para uma figura específica se não houver dados válidos para plotá-la.
    """
    # Extrai os dados da resposta da LLM processando todas as linhas de categoria CIF
    target_lines = extrair_linhas_categoria_cif_regex(llm_res)
    data_by_group = count_group_frequencies(target_lines)
    df_group = pd.DataFrame(data_by_group.items(), columns=['Componente CIF', 'Frequencia'])
    data_individual_codes = count_individual_frequencies(target_lines)
    df_individual_treemap = create_treemap_dataframe(data_individual_codes)

    translation_map = {
    'count': 'Contagem',
    'mean': 'Média',
    'std': 'Desvio Padrão',
    'min': 'Mínimo',
    '25%': '25º Percentil',
    '50%': 'Mediana (50%)',
    '75%': '75º Percentil',
    'max': 'Máximo'
    }

    df_group_describe = df_group.describe().reset_index()
    df_group_describe = df_group_describe.rename(columns={'index': 'Estatística'})
    df_group_describe['Estatística'] = df_group_describe['Estatística'].replace(translation_map)
    df_treemap_describe = df_group.describe().reset_index()
    df_treemap_describe = df_treemap_describe.rename(columns={'index': 'Estatística'})
    df_treemap_describe['Estatística'] = df_treemap_describe['Estatística'].replace(translation_map)

    # Cria os gráficos com os dados extraídos
    fig_pie = create_pie_graph(data_by_group, titulo="Distribuição da Classificação por Componentes CIF")
    fig_bar = create_bar_graph(data_by_group, titulo="Frequência da Classificação por Componentes CIF")
    fig_tree_map = create_tree_map_graph(df_individual_treemap, titulo="Treemap de Frequência por Código CIF")

    temp_file = generate_pdf_report_temp(
        plotly_figs=[fig_pie, fig_bar, fig_tree_map],
        dataframes=[df_group, df_group_describe, df_individual_treemap, df_treemap_describe],
        text=llm_res,
        titulo_relatorio="Relatório de Classificação por Componentes CIF"
        )

    return df_group, df_group_describe, df_individual_treemap, df_treemap_describe, fig_pie, fig_bar, fig_tree_map, temp_file

def extrair_linhas_categoria_cif_regex(texto):
    """
    Extrai do texto apenas as linhas que contêm "Categoria CIF:" usando regex.

    Args:
        texto (str): O texto de entrada contendo várias linhas.

    Returns:
        str: Uma string contendo apenas as linhas "Categoria CIF:", separadas por quebras de linha.
    """
    # Compila a regex para encontrar qualquer linha que contenha "Categoria CIF:"
    # re.M (re.MULTILINE) faz com que ^ e $ correspondam ao início/fim de cada linha
    # em vez de apenas o início/fim da string inteira.
    # r"^.*Categoria CIF:.*$" significa:
    # ^   - Início da linha
    # .* - Zero ou mais caracteres (qualquer coisa)
    # Categoria CIF: - A string literal "Categoria CIF:"
    # .* - Zero ou mais caracteres (qualquer coisa)
    # $   - Fim da linha
    padrao = re.compile(r"^.*Categoria CIF:.*$", re.M)
    
    # Encontra todas as ocorrências que correspondem ao padrão
    linhas_cif_encontradas = re.findall(padrao, texto)
    
    return '\n'.join(linhas_cif_encontradas)

def count_group_frequencies(llm_res: str) -> Dict[str, int]:
    """
    Calcula a frequência acumulada de cada grupo de componentes CIF (b, d, e, s, Outros)
    a partir de todas as linhas "Categoria CIF:" encontradas na resposta da LLM.

    Args:
        llm_res (str): A resposta completa da LLM.

    Returns:
        Dict[str, int]: Um dicionário com a frequência acumulada de cada grupo de componentes.
    """
    group_frequencies: Dict[str, int] = {label: 0 for label in CIF_COMPONENTS.values()}
    print('group_frequencies: ', group_frequencies)

    # Encontra todas as linhas de "Categoria CIF: ..."
    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)    

    if not all_cif_category_lines:
        return group_frequencies # Retorna zerado se nenhuma linha CIF for encontrada

    for cif_category_line in all_cif_category_lines:
        # Contagem para códigos CIF numéricos (b, d, e, s) na linha atual
        numeric_matches = re.findall(CIF_NUMERIC_CODE_REGEX, cif_category_line)
        for prefix, _ in numeric_matches:
            component_name = CIF_COMPONENTS.get(prefix.lower())
            if component_name and component_name != CIF_COMPONENTS['Outros']: # Evita dupla contagem se 'Outros' for um prefixo
                group_frequencies[component_name] += 1

        # Contagem das ocorrências para códigos especiais (N.D., N.C., N/A) na linha atual
        special_code_matches = re.findall(COMBINED_SPECIAL_CODES_REGEX, cif_category_line)
        if special_code_matches:
            group_frequencies[CIF_COMPONENTS['Outros']] += len(special_code_matches)

    return group_frequencies

def count_individual_frequencies(llm_res: str) -> Dict[str, int]:
    """
    Conta a frequência acumulada de cada código CIF individual (ex: b123, d456, N.D.)
    a partir de todas as linhas "Categoria CIF:" encontradas na resposta da LLM.

    Args:
        llm_res (str): A resposta completa da LLM.

    Returns:
        Dict[str, int]: Um dicionário com a frequência acumulada de cada código individual.
    """
    individual_frequencies: Dict[str, int] = {}

    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)

    if not all_cif_category_lines:
        return individual_frequencies

    for cif_category_line in all_cif_category_lines:
        # Contagem para códigos CIF numéricos completos (ex: b123) na linha atual
        numeric_code_matches = re.findall(CIF_FULL_NUMERIC_CODE_REGEX, cif_category_line)
        for code in numeric_code_matches:
            code_lower = code.lower()
            individual_frequencies[code_lower] = individual_frequencies.get(code_lower, 0) + 1

        # Contagem para códigos especiais individuais (N.D., N.C., N/A) na linha atual
        for special_code_literal in SPECIAL_CODE_LITERALS:
            pattern = re.escape(special_code_literal)
            matches = re.findall(pattern, cif_category_line)
            if matches:
                individual_frequencies[special_code_literal] = \
                    individual_frequencies.get(special_code_literal, 0) + len(matches)
            
    return individual_frequencies

def create_treemap_dataframe(data_dict: dict) -> pd.DataFrame:
    """
    Cria um DataFrame formatado para treemaps do Plotly a partir de um dicionário
    de códigos e frequências, inferindo a hierarquia 'Parent', 'Subparent' e 'Filho'.

    Args:
        data_dict (dict): Um dicionário onde as chaves são os códigos (ex: 'd920')
                          e os valores são suas frequências.

    Returns:
        pd.DataFrame: Um DataFrame com as colunas 'Parent', 'Subparent', 'Filho'
                      e 'Frequencia', pronto para uso com px.treemap(path=...).
    """
    # 1. Converter o dicionário diretamente para um DataFrame com 'Filho' e 'Frequencia'
    # 'Filho' já representa o código completo original
    df = pd.DataFrame(list(data_dict.items()), columns=['Filho', 'Frequencia'])

    # Listas para armazenar os componentes da hierarquia
    parents = []
    subparents = []

    # 2. Iterar sobre cada 'Filho' para derivar a hierarquia
    for index, row in df.iterrows():
        code = str(row['Filho']) # O 'Filho' é o código completo original

        parent = 'Outros'
        subparent = 'Outros'
        # 'filho' já está na coluna 'Filho' do DataFrame

        if code.startswith('s'):
            parent = 's'
        elif code.startswith('d'):
            parent = 'd'
        elif code.startswith('b'):
            parent = 'b'
        elif code.startswith('e'):
            parent = 'e'

        # Extrair o subparent (o primeiro dígito após a letra)
        match = re.match(r'[sdbbe]([0-9])', code)
        if match:
            subparent = parent + match.group(1)
        elif parent != 'Outros' and len(code) > 1 and code[1:].isdigit():
            # Caso como 's1' onde o '1' já é o subparent
            subparent = parent + code[1]

        parents.append(parent)
        subparents.append(subparent)

    # Adicionar as novas colunas ao DataFrame
    df['Parent'] = parents
    df['Subparent'] = subparents

    # Selecionar, reordenar e ordenar as colunas para o `path`
    # Não precisamos mais de df_treemap = df[['Parent', 'Subparent', 'Filho', 'Frequencia']]
    # porque o DataFrame 'df' já contém as colunas necessárias e na ordem correta,
    # exceto pela ordenação.
    df_treemap = df.sort_values(by=['Parent', 'Subparent', 'Filho']).reset_index(drop=True)

    return df_treemap