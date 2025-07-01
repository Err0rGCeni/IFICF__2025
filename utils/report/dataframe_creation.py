# utils/report/dataframe_creation.py
import re
import pandas as pd
from typing import Dict, Tuple, List

from .icf_categories import ICFComponent

# Padrões Regex e Constantes para extração (movidos para cá)
SPECIAL_CODE_LITERALS: List[str] = ['N.D.', 'N.C.', 'N/A'] # Usado para contagem individual
# Regex para capturar códigos CIF numéricos (prefixo e número)
CIF_NUMERIC_CODE_REGEX: str = r'([bdes])([0-9]+)'
# Regex para capturar códigos CIF numéricos completos (código inteiro)
CIF_FULL_NUMERIC_CODE_REGEX: str = r'([bdes][0-9]+)'
# Regex para encontrar todas as linhas de Categoria CIF
ALL_CIF_CATEGORY_LINES_REGEX: str = r"Codificação CIF: (.+)"

def _count_group_frequencies(llm_res: str) -> Dict[str, int]:
    """Conta a frequência dos grupos CIF principais e códigos especiais."""
    print("Contando frequências por grupo...")
    # Inicializa as frequências com base nos rótulos da Enum ICFComponent
    group_frequencies: Dict[str, int] = {member.label: 0 for member in ICFComponent}

    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)
    if not all_cif_category_lines:
        return group_frequencies

    for cif_category_line in all_cif_category_lines:
        # Contagem para códigos numéricos (b, d, e, s)
        numeric_matches = re.findall(CIF_NUMERIC_CODE_REGEX, cif_category_line)
        for prefix, _ in numeric_matches:
            try:
                component = ICFComponent.from_short_code(prefix.lower())
                group_frequencies[component.label] += 1
            except ValueError:
                print(f"Aviso: Prefixo CIF numérico não reconhecido '{prefix}' na linha: {cif_category_line}")

        # Contagem específica para códigos especiais
        if re.search(re.escape('N.C.'), cif_category_line):
            group_frequencies[ICFComponent.NOT_COVERED.label] += len(re.findall(re.escape('N.C.'), cif_category_line))
        
        if re.search(re.escape('N.D.'), cif_category_line):
            group_frequencies[ICFComponent.NOT_DEFINED.label] += len(re.findall(re.escape('N.D.'), cif_category_line))
        
        # Assumindo que N/A também conta como "Não Definido" para fins de agrupamento
        if re.search(re.escape('N/A'), cif_category_line):
            group_frequencies[ICFComponent.NOT_DEFINED.label] += len(re.findall(re.escape('N/A'), cif_category_line))
            
    print(f"Frequências por grupo atualizadas: {group_frequencies}")
    return group_frequencies

def _count_individual_frequencies(llm_res: str) -> Dict[str, int]:
    """Conta a frequência de cada código CIF individualmente."""
    print("Contando frequências individuais...")
    individual_frequencies: Dict[str, int] = {}
    all_cif_category_lines = re.findall(ALL_CIF_CATEGORY_LINES_REGEX, llm_res)

    if not all_cif_category_lines:
        return individual_frequencies

    for cif_category_line in all_cif_category_lines:
        # Códigos numéricos completos (ex: b123, d45)
        numeric_code_matches = re.findall(CIF_FULL_NUMERIC_CODE_REGEX, cif_category_line)
        for code in numeric_code_matches:
            code_lower = code.lower()
            individual_frequencies[code_lower] = individual_frequencies.get(code_lower, 0) + 1

        # Códigos literais especiais (N.D., N.C., N/A)
        for special_code_literal in SPECIAL_CODE_LITERALS:
            # Escapa o literal para uso seguro em regex e garante que seja tratado como string literal
            pattern = re.escape(special_code_literal)
            matches = re.findall(pattern, cif_category_line)
            if matches:
                # Usa o literal original (ex: "N.C.") como chave
                individual_frequencies[special_code_literal] = \
                    individual_frequencies.get(special_code_literal, 0) + len(matches)
                    
    print(f"Frequências individuais atualizadas: {individual_frequencies}")
    return individual_frequencies

def _create_treemap_dataframe(data_dict: Dict[str, int]) -> pd.DataFrame:
    """Cria o DataFrame para o gráfico Treemap, definindo Componente, Capítulo e Código."""
    print("Criando DataFrame para Treemap com novos nomes de coluna...")
    # Renomeando colunas na criação inicial do DataFrame
    df = pd.DataFrame(list(data_dict.items()), columns=['Código', 'Frequência'])

    parents_list = []
    subparents_list = [] # Esta será a coluna 'Capítulo'

    nc_short_code = ICFComponent.NOT_COVERED.short_code
    nd_short_code = ICFComponent.NOT_DEFINED.short_code
    numeric_prefixes = {
        ICFComponent.BODY_FUNCTIONS.short_code,
        ICFComponent.ACTIVITIES_PARTICIPATION.short_code,
        ICFComponent.ENVIRONMENT.short_code,
        ICFComponent.BODY_STRUCTURES.short_code
    }

    for _, row in df.iterrows():
        code_filho = str(row['Código']).lower() # Usa a nova coluna 'Código'
        componente_val = None # Esta será a coluna 'Componente'
        capitulo_val = code_filho 

        if code_filho.startswith(tuple(numeric_prefixes)):
            prefix = code_filho[0]
            componente_val = prefix 

            match_chapter = re.match(rf"({prefix})([0-9])", code_filho)
            if match_chapter:
                capitulo_val = match_chapter.group(0)
            elif len(code_filho) == 1:
                capitulo_val = prefix
        elif code_filho == 'n.c.':
            componente_val = nc_short_code
            capitulo_val = nc_short_code 
        elif code_filho == 'n.d.':
            componente_val = nd_short_code
            capitulo_val = nd_short_code
        elif code_filho == 'n/a':
            componente_val = nd_short_code
            capitulo_val = nd_short_code
        else:
            print(f"Aviso: Código '{code_filho}' não mapeado para Componente no treemap. Atribuindo a '{nd_short_code}'.")
            componente_val = nd_short_code
            capitulo_val = nd_short_code

        parents_list.append(componente_val)
        subparents_list.append(capitulo_val)

    # Renomeando colunas ao atribuir as listas
    df['Componente'] = parents_list
    df['Capítulo'] = subparents_list

    all_nodes_in_hierarchy = set(df['Componente']).union(set(df['Capítulo']))
    existing_codigos = set(df['Código']) # Usa a nova coluna 'Código'

    new_rows_for_hierarchy = []
    for node in all_nodes_in_hierarchy:
        if node not in existing_codigos and node is not None:
            node_parent_for_hierarchy = "" 
            node_subparent_for_hierarchy = node

            if node.startswith(tuple(numeric_prefixes)) and len(node) > 1 and node[1:].isdigit():
                node_parent_for_hierarchy = node[0]

            # Usando os novos nomes de coluna ao adicionar linhas hierárquicas
            new_rows_for_hierarchy.append({
                'Código': node, 
                'Frequência': 0, 
                'Componente': node_parent_for_hierarchy,
                'Capítulo': node_subparent_for_hierarchy
            })

    if new_rows_for_hierarchy:
        df_new_rows = pd.DataFrame(new_rows_for_hierarchy)
        df = pd.concat([df, df_new_rows], ignore_index=True)

    # Usando os novos nomes de coluna para ordenação
    df_treemap = df.sort_values(by=['Componente', 'Capítulo', 'Código']).reset_index(drop=True)
    return df_treemap

def process_report_data(llm_res: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Processa a resposta da LLM para extrair dados e criar os DataFrames do relatório.
    Utiliza a enumeração ICFComponent para mapeamento de categorias.
    Nomes de coluna atualizados para 'Código', 'Frequência', 'Componente', 'Capítulo'.
    """
    print("Processando dados para DataFrames com nomes de coluna atualizados...")

    data_by_group = _count_group_frequencies(llm_res)
    # Usando 'Frequência' com acento
    df_group = pd.DataFrame(list(data_by_group.items()), columns=['Componente CIF', 'Frequência'])
    ordered_labels = ICFComponent.get_ordered_labels()
    df_group['Componente CIF'] = pd.Categorical(df_group['Componente CIF'], categories=ordered_labels, ordered=True)
    df_group = df_group.sort_values('Componente CIF').reset_index(drop=True)

    data_individual_codes = _count_individual_frequencies(llm_res)
    # df_individual_treemap já usa os novos nomes de _create_treemap_dataframe
    df_individual_treemap = _create_treemap_dataframe(data_individual_codes)

    translation_map = {
        'count': 'Contagem', 'mean': 'Média', 'std': 'Desvio Padrão',
        'min': 'Mínimo', '25%': '25º Percentil', '50%': 'Mediana (50%)',
        '75%': '75º Percentil', 'max': 'Máximo'
    }

    # Describe para df_group usando 'Frequência'
    df_group_describe = df_group[['Frequência']].describe().reset_index()
    df_group_describe = df_group_describe.rename(columns={'index': 'Estatística'})
    df_group_describe['Estatística'] = df_group_describe['Estatística'].replace(translation_map)

    # Describe para df_individual_treemap usando 'Frequência'
    df_treemap_describe = df_individual_treemap[df_individual_treemap['Frequência'] > 0][['Frequência']].describe().reset_index()
    df_treemap_describe = df_treemap_describe.rename(columns={'index': 'Estatística'})
    df_treemap_describe['Estatística'] = df_treemap_describe['Estatística'].replace(translation_map)

    return df_group, df_group_describe, df_individual_treemap, df_treemap_describe