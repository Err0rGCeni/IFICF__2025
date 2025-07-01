# utils/report/icf_categories.py
from enum import Enum
from typing import List, Dict

class ICFComponent(Enum):
    """
    Representa os componentes da Classificação Internacional de Funcionalidade (CIF)
    com seus respectivos códigos, rótulos e cores.
    """
    # Membros da enumeração: NOME_PYTHON = (código_curto, rótulo_completo, cor_hex)
    BODY_FUNCTIONS = ('b', 'Funções Corporais (b)', '#3E7CB1')
    ACTIVITIES_PARTICIPATION = ('d', 'Atividades e Participação (d)', '#D41A80')
    ENVIRONMENT = ('e', 'Ambiente (e)', '#1AD41A')
    BODY_STRUCTURES = ('s', 'Estruturas Corporais (s)', '#FFBF00')
    NOT_COVERED = ('nc', 'Não Coberto (n.c.)', '#B33F31')
    NOT_DEFINED = ('nd', 'Não Definido (n.d.)', '#E88C80')

    def __init__(self, short_code: str, label: str, color: str):
        self._short_code = short_code
        self._label = label
        self._color = color

    @property
    def short_code(self) -> str:
        """Código curto do componente CIF (ex: 'b', 'd', 'nc')."""
        return self._short_code

    @property
    def label(self) -> str:
        """Rótulo completo e descritivo do componente CIF."""
        return self._label

    @property
    def color(self) -> str:
        """Cor hexadecimal associada ao componente para gráficos."""
        return self._color

    @classmethod
    def from_short_code(cls, code: str) -> 'ICFComponent':
        """
        Retorna o membro ICFComponent correspondente ao código curto fornecido.
        Levanta um ValueError se o código não for encontrado.
        """
        for member in cls:
            if member.short_code == code.lower(): # Comparação case-insensitive para códigos
                return member
        raise ValueError(f"Nenhum componente CIF encontrado para o código curto: '{code}'")

    @classmethod
    def from_label(cls, label_to_find: str) -> 'ICFComponent':
        """
        Retorna o membro ICFComponent correspondente ao rótulo completo fornecido.
        Levanta um ValueError se o rótulo não for encontrado.
        """
        for member in cls:
            if member.label == label_to_find:
                return member
        raise ValueError(f"Nenhum componente CIF encontrado para o rótulo: '{label_to_find}'")

    # Métodos para gerar as estruturas de dados originais (se necessário para compatibilidade)
    @classmethod
    def get_ordered_labels(cls) -> List[str]:
        """Retorna uma lista ordenada dos rótulos dos componentes CIF."""
        return [member.label for member in cls]

    @classmethod
    def get_color_map(cls) -> Dict[str, str]:
        """Retorna um dicionário mapeando rótulos de componentes CIF para suas cores."""
        return {member.label: member.color for member in cls}

    @classmethod
    def get_short_code_to_label_map(cls) -> Dict[str, str]:
        """Retorna um dicionário mapeando códigos curtos para rótulos completos."""
        return {member.short_code: member.label for member in cls}

    @classmethod
    def get_short_code_to_component_map(cls) -> Dict[str, 'ICFComponent']:
        """Retorna um dicionário mapeando códigos curtos para os membros ICFComponent."""
        return {member.short_code: member for member in cls}