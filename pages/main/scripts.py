# pages/main/scripts.py
import time
import gradio as gr
from typing import Any, Generator, Dict

from utils.apis.gemini import api_generate
from .strings import STRINGS

def process_inputs_to_api(user_input: Dict[str, Any]) -> Generator[tuple, None, None]:
    """
    Processa a entrada do usuário (texto ou arquivo) com a API do Gemini.

    Esta função serve como o handler para a interface Gradio. Ela lê o estado
    'user_input', que contém o tipo e o conteúdo da entrada, para então
    chamar o backend.

    Args:
        user_input (Dict[str, Any]): Um dicionário vindo de um gr.State com as chaves
                                     "type" ('text' ou 'file') e "content" (o texto
                                     ou o caminho do arquivo).

    Yields:
        Atualizações para os componentes da interface do Gradio.
    """
    current_symbol = " ♾️"  # Símbolo de processamento
    formatted_output = ""
    status_message = STRINGS["TXTBOX_STATUS_IDLE"]

    # --- Ação 1: Atualiza a UI para mostrar que o processamento começou ---
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value="", interactive=False),
        gr.update(selected=1),  # Muda para a aba de resultados
        gr.update(label=STRINGS["TAB_1_TITLE"] + current_symbol, interactive=True)
    )

    try:
        # --- Ação 2: Lógica de validação da entrada vinda do 'gr.State' ---
        input_type = user_input.get("type")
        content = user_input.get("content")

        if not input_type or not content:
            raise ValueError("Nenhuma entrada fornecida. Por favor, digite um texto ou faça o upload de um arquivo.")

        # --- Ação 3: Chama o backend com o parâmetro correto ---
        params_para_api = {}
        if input_type == "text":
            print(f"Processando via texto: \"{content[:100]}...\"")
            params_para_api['input_text'] = content
        elif input_type == "file":
            # 'content' já é o caminho do arquivo temporário
            print(f"Processando via arquivo: {content}")
            params_para_api['input_file'] = content
        else:
            # Caso o estado 'user_input' tenha um tipo inesperado
            raise ValueError(f"Tipo de entrada desconhecido: '{input_type}'")


        # Chama a função de backend com os parâmetros corretos
        time.sleep(2)
        #TODO llm_response = api_generate(**params_para_api)
        llm_response = '''
        - Frase de Entrada: Tosse.
        - Conceito Significativo: Tosse
        - Status de Cobertura pela CIF: Não Coberto (N.C.)
        - Categoria CIF: N.C.
        - Codificação CIF: N.C.
        - Descrição CIF: N.C.
        - Justificativa da Classificação: A tosse não consta explicitamente no contexto RAG, nem está descrita de forma que possa ser vinculada a uma categoria específica da CIF.

        - Frase de Entrada: O paciente sente dores abdominais agudas, localizadas principalmente na região inferior do abdômen.
        - Conceito Significativo: Dores abdominais agudas
        - Status de Cobertura pela CIF: Coberto
        - Categoria CIF: Funções Corporais
        - Codificação CIF: b28012 - Dor no estômago ou abdome
        - Descrição CIF: Sensação desagradável sentida no estômago ou no abdome que indica lesão potencial ou real de alguma estrutura do corpo. Inclui: dor na regido pélvica.
        - Justificativa da Classificação: A descrição de dores abdominais se encaixa na categoria de "Dor localizada" nas Funções Corporais, especificamente "Dor no estômago ou abdome".

        - Frase de Entrada: Fadiga.
        - Conceito Significativo: Fadiga
        - Status de Cobertura pela CIF: Coberto
        - Categoria CIF: Funções Corporais
        - Codificação CIF: b4552 - Fadiga
        - Descrição CIF: Funções relacionadas à suscetibilidade à fadiga, cm qualquer nível de exercício.
        - Justificativa da Classificação: O termo "Fadiga" é diretamente mencionado na CIF como parte das "Funções de tolerância a exercícios".
        '''

        status_message = STRINGS["TXTBOX_STATUS_OK"]
        formatted_output = f"--- Resposta Fornecida pela LLM ---\n{llm_response}\n"
        current_symbol = " ✅"

    except Exception as e:
        # Captura qualquer erro (de validação ou da API) e o exibe na UI
        status_message = STRINGS["TXTBOX_STATUS_ERROR"]
        formatted_output = f"\n--- Erro ao Processar ---\nDetalhes: {e}"
        current_symbol = " ⚠️"
        print(f"ERRO na interface Gradio: {e}") # Loga o erro completo no console

    # --- Ação Final: Retorna o resultado (sucesso ou erro) para a UI ---
    yield (
        gr.update(value=status_message, interactive=False),
        gr.update(value=formatted_output, interactive=True), # Permite copiar o resultado
        gr.update(),
        gr.update(label=STRINGS["TAB_1_TITLE"] + current_symbol, interactive=True)
    )