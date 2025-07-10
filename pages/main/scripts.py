# pages/main/scripts.py
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Generator, Dict, Tuple, Optional

from utils.apis.gemini import api_generate
from utils.report.report_creation import generate_report_pdf
from utils.report.graph_creation import create_report_plots
from utils.report.dataframe_creation import process_report_data
from .strings import STRINGS

RADIO_OPT = {
    "text": {
        "id": "text",
        "icon": "✍️",
        "description": "Inserir texto",
        "label": "✍️ Inserir texto"
    },
    "file": {
        "id": "file",
        "icon": "📚",
        "description": "Enviar arquivo",
        "label": "📚 Enviar arquivo"
    }
}

class InputTabFn:
    """Agrupa os callbacks da aba de entrada de dados (Tab 0)."""

    @staticmethod
    def update_input_visibility(option: str, text_input: str, file_input: Any) -> Tuple[gr.TabItem, gr.Textbox, gr.File, gr.Button]:
        """
        Alterna a visibilidade dos campos de entrada (texto ou arquivo) com base na escolha do usuário.

        Args:
            option (str): O valor do componente de rádio ('text' ou 'file').
            text_input (str): O conteúdo atual do campo de texto.
            file_input (Any): O objeto do arquivo carregado.

        Returns:
            Tuple[gr.TabItem, gr.Textbox, gr.File, gr.Button]: Uma tupla de atualizações para os componentes do Gradio:
                - gr.update: Atualiza o rótulo da aba com o ícone correspondente.
                - gr.update: Define a visibilidade do campo de texto.
                - gr.update: Define a visibilidade do campo de upload de arquivo.
                - gr.update: Habilita ou desabilita o botão de processar com base na validação da entrada.
        """
        if option == RADIO_OPT["text"]["id"]:
            symbol = RADIO_OPT["text"]["icon"]
            return (
                gr.update(label=f"{STRINGS['TAB_0_TITLE']} {symbol}"),
                gr.update(visible=True),
                gr.update(visible=False),
                InputTabFn.text_input_validator(text_input)
            )

        elif option == RADIO_OPT["file"]["id"]:
            symbol = RADIO_OPT["file"]["icon"]
            return (
                gr.update(label=f"{STRINGS['TAB_0_TITLE']} {symbol}"),
                gr.update(visible=False),
                gr.update(visible=True),
                InputTabFn.file_input_validator(file_input)
            )

        else:
            return (
                gr.skip(),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.skip()
            )

    @staticmethod
    def file_input_validator(file_obj: Any) -> gr.Button:
        """
        Valida se um arquivo foi carregado para habilitar o botão de processamento.

        Args:
            file_obj (Any): O objeto de arquivo do componente gr.File.

        Returns:
            gr.Button: Um componente de botão atualizado (habilitado se o arquivo existir, senão desabilitado).
        """
        if file_obj is not None:
            return gr.update(interactive=True)
        else:
            return gr.update(interactive=False)

    @staticmethod
    def text_input_validator(text: str) -> gr.Button:
        """
        Valida se o texto inserido tem mais de 4 caracteres para habilitar o botão.

        Args:
            text (str): O texto do componente gr.Textbox.

        Returns:
            gr.Button: Um componente de botão atualizado (habilitado se o texto for válido, senão desabilitado).
        """
        if text is not None and len(text.strip()) > 4:
            return gr.update(interactive=True)
        else:
            return gr.update(interactive=False)

    @staticmethod
    def handle_process_button_click(radio_value: str, text_input: str, file_input: Any) -> Tuple[Dict[str, Any], gr.TabItem, gr.Tabs]:
        """
        Armazena a entrada do usuário no estado e navega para a aba de resultados.

        Esta função é acionada pelo clique no botão de processar. Ela consolida
        a entrada do usuário em um dicionário e o armazena em um `gr.State` para
        uso posterior.

        Args:
            radio_value (str): A opção selecionada ('text' ou 'file').
            text_input (str): O conteúdo do campo de texto.
            file_input (Any): O objeto de arquivo carregado.

        Returns:
            Tuple[Dict[str, Any], gr.TabItem, gr.Tabs]: Uma tupla de atualizações para a interface:
                - Dict: O dicionário com os dados do usuário a ser salvo no estado (`gr.State`).
                - gr.update: Habilita e atualiza o rótulo da aba de resultados.
                - gr.update: Alterna a visualização para a aba de resultados.
        """
        user_input = {
            "type": radio_value,
            "content": text_input if radio_value == RADIO_OPT["text"]["id"] else file_input
        }
        return (
            user_input,
            gr.update(label=STRINGS["TAB_1_TITLE"], interactive=True),
            gr.update(selected=1)
        )

class ResultsTabFn:
    """Agrupa os callbacks da aba de resultados (Tab 1)."""

    @staticmethod
    def handle_status_text_change(status_text: str) -> gr.Button:
        """
        Habilita o botão de criar relatório se o status do processamento for 'OK'.

        Args:
            status_text (str): O texto do campo de status.

        Returns:
            gr.Button: Um botão atualizado, habilitado e com estilo 'primary' se o status for OK.
        """
        if status_text == STRINGS["TXTBOX_STATUS_OK"]:
            return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
        else:
            return gr.update(value=STRINGS["BTN_CREATE_REPORT_LABEL_DISABLED"], interactive=False, variant="secondary")

    @staticmethod
    def switch_to_report_tab() -> Tuple[gr.Tabs, gr.TabItem]:
        """
        Navega para a aba de relatório e a torna interativa.

        Returns:
            Tuple[gr.Tabs, gr.TabItem]:
                - gr.update: Alterna a visualização para a aba de relatório (índice 2).
                - gr.update: Habilita e atualiza o rótulo da aba de relatório.
        """
        return gr.update(selected=2), gr.update(label=STRINGS["TAB_2_TITLE"] + " ✅", interactive=True)

    @staticmethod
    def process_inputs_to_api(user_input: Dict[str, Any]) -> Generator[Tuple[gr.Textbox, gr.Textbox, gr.Tabs, gr.TabItem], None, None]:
        """
        Processa a entrada do usuário, chama a API externa e atualiza a UI em etapas.

        Esta função geradora orquestra o fluxo de processamento:
        1. Atualiza a UI para indicar o início do processamento.
        2. Valida a entrada e chama a API do Gemini.
        3. Em caso de sucesso ou erro, atualiza a UI com o resultado final.

        Args:
            user_input (Dict[str, Any]): Dicionário vindo do `gr.State`, contendo
                as chaves "type" e "content".

        Yields:
            Tuple[gr.Textbox, gr.Textbox, gr.Tabs, gr.TabItem]: Tuplas de atualizações para os componentes de Gradio
            (status, caixa de saída, abas e rótulo da aba) em cada etapa do processo.
        """
        symbol = " ♾️"
        status_message = STRINGS["TXTBOX_STATUS_IDLE"]

        # Etapa 1: Sinaliza que o processamento começou
        yield (
            gr.update(value=status_message, interactive=False),
            gr.update(value="", interactive=False),
            gr.update(selected=1),
            gr.update(label=STRINGS["TAB_1_TITLE"] + symbol, interactive=True)
        )

        try:
            # Etapa 2: Valida e processa a entrada
            input_type = user_input.get("type")
            content = user_input.get("content")

            if not input_type or not content:
                raise ValueError("Nenhuma entrada fornecida. Por favor, insira um texto ou envie um arquivo.")

            llm_response = api_generate(user_input=user_input)
            status_message = STRINGS["TXTBOX_STATUS_OK"]
            formatted_output = f"--- Resposta da LLM ---\n{llm_response}\n"
            symbol = " ✅"

        except Exception as e:
            status_message = STRINGS["TXTBOX_STATUS_ERROR"]
            formatted_output = f"\n--- Erro ao Processar ---\nDetalhes: {e}"
            symbol = " ⚠️"
            print(f"ERRO na interface Gradio: {e}")

        # Etapa Final: Retorna o resultado para a UI
        yield (
            gr.update(value=status_message, interactive=False),
            gr.update(value=formatted_output, interactive=True),
            gr.update(),
            gr.update(label=STRINGS["TAB_1_TITLE"] + symbol, interactive=True)
        )

class ReportTabFn:
    """Agrupa os callbacks da aba de relatório (Tab 2)."""

    @staticmethod
    def update_dataframe_components(df_dict: Dict[str, pd.DataFrame]) -> Tuple[gr.DataFrame, gr.DataFrame, gr.DataFrame, gr.DataFrame]:
        """
        Atualiza os componentes de DataFrame na UI com os dados processados.

        Args:
            df_dict (Dict[str, pd.DataFrame]): Dicionário contendo os DataFrames gerados.

        Returns:
            Tuple contendo quatro componentes gr.DataFrame atualizados.
        """
        return (
            gr.DataFrame(value=df_dict["group_data"]),
            gr.DataFrame(value=df_dict["group_description"]),
            gr.DataFrame(value=df_dict["individuals_data"]),
            gr.DataFrame(value=df_dict["individuals_description"])
        )

    @staticmethod
    def process_report_data_wrapper(llm_response: str) -> Dict[str, pd.DataFrame]:
        """
        Encapsula a lógica de extração e processamento de dados da resposta da LLM.

        Args:
            llm_response (str): A resposta em texto plano da LLM.

        Returns:
            Dict[str, pd.DataFrame]: Um dicionário com os DataFrames prontos para visualização.
        """
        print(f"Processando dados do relatório...\n{llm_response[:100]}...")
        df_group, df_group_describe, df_individual_treemap, df_treemap_describe = process_report_data(llm_res=llm_response)

        return {
            "group_data": df_group,
            "group_description": df_group_describe,
            "individuals_data": df_individual_treemap,
            "individuals_description": df_treemap_describe
        }

    @staticmethod
    def report_plots_wrapper(df_dict: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
        """
        Gera os gráficos a partir dos DataFrames processados.

        Args:
            df_dict (Dict[str, pd.DataFrame]): Dicionário com os DataFrames do relatório.

        Returns:
            Dict[str, go.Figure]: Um dicionário com as figuras Plotly geradas.
        """
        df_group = df_dict["group_data"]
        df_individuals = df_dict["individuals_data"]
        pie_chart, bar_chart, tree_map = create_report_plots(df_group, df_individuals)

        return {
            "pie_chart": pie_chart,
            "bar_chart": bar_chart,
            "tree_map": tree_map
        }

    @staticmethod
    def update_plot_components(go_dict: Dict[str, go.Figure]) -> Tuple[gr.Plot, gr.Plot, gr.Plot]:
        """
        Atualiza os componentes de gráfico na UI com as figuras geradas.

        Args:
            go_dict (Dict[str, go.Figure]): Dicionário contendo as figuras Plotly.

        Returns:
            Tuple contendo três componentes gr.Plot atualizados.
        """
        return (
            gr.Plot(value=go_dict["pie_chart"]),
            gr.Plot(value=go_dict["bar_chart"]),
            gr.Plot(value=go_dict["tree_map"])
        )

    @staticmethod
    def update_download_button_component(report_file_path: Optional[str]) -> gr.DownloadButton:
        """
        Atualiza o botão de download com o caminho do relatório PDF gerado.

        Args:
            report_file_path (Optional[str]): O caminho para o arquivo PDF, ou None se houve erro.

        Returns:
            gr.DownloadButton: O botão de download atualizado, habilitado com o caminho do arquivo
            ou desabilitado em caso de falha.
        """
        if report_file_path:
            return gr.update(value=report_file_path, label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ENABLED"], interactive=True, variant="primary")
        else:
            return gr.update(label=STRINGS["DOWNLOAD_BTN_REPORT_LABEL_ERROR"], interactive=False, variant="secondary")

    @staticmethod
    def generate_report_pdf_wrapper(llm_res: str, df_dict: Dict[str, pd.DataFrame], go_dict: Dict[str, go.Figure]) -> str:
        """
        Orquestra a geração do arquivo PDF do relatório e retorna seu caminho.

        Args:
            llm_res (str): A resposta original da LLM.
            df_dict (Dict[str, pd.DataFrame]): Dicionário com os DataFrames do relatório.
            go_dict (Dict[str, go.Figure]): Dicionário com as figuras Plotly do relatório.

        Returns:
            str: O caminho do arquivo PDF temporário gerado.
        """
        temp_path = generate_report_pdf(
            llm_res=llm_res,
            df_group=df_dict["group_data"],
            df_group_describe=df_dict["group_description"],
            df_individual_treemap=df_dict["individuals_data"],
            df_treemap_describe=df_dict["individuals_description"],
            fig_pie=go_dict["pie_chart"],
            fig_bar=go_dict["bar_chart"],
            fig_tree_map=go_dict["tree_map"]
        )
        return temp_path