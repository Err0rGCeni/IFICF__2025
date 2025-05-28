import re
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple, Optional, List

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

def generate_report(llm_res: str) -> Tuple[Optional[go.Figure], Optional[go.Figure]]:
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
    print('target_lines: ', target_lines)
    data_by_group = count_group_frequencies(target_lines)
    print('data_by_group: ', data_by_group)
    data_individual_codes = count_individual_frequencies(target_lines) # Descomente se precisar usar
    print('data_individual_codes: ', data_individual_codes)
    # data_individual_codes = count_individual_frequencies(llm_res) # Descomente se precisar usar

    # Cria os gráficos com os dados extraídos
    fig_pie = create_pie_graph(data_by_group, titulo="Distribuição da Classificação por Componentes CIF")
    fig_bar = create_bar_graph(data_by_group, titulo="Frequência da Classificação por Componentes CIF")

    return fig_pie, fig_bar

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
