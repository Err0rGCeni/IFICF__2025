import re
import gradio as gr
from utils.rag_retriever import inicializar_rag
from utils.llm_response import res_generate_API # A função unificada agora trata as estratégias de RAG e LLM

# --- Configurações Iniciais do RAG ---
documentos, index, embedder = inicializar_rag()

# --- Constantes de Interface ---
LABELS = {
    "APP_TITLE": "Sistema RAG para Análise de Documentos",
    "APP_DESCRIPTION": "Processe frases individualmente ou envie um arquivo para análise em lote usando um sistema RAG.",
    "TAB_INPUT_TITLE": "Entrada de Frases",
    "TAB_RESULTS_TITLE": "Resultados da Análise",
    "INPUT_FILE_LABEL": "Carregar Arquivo (.txt, .pdf, .docx)",
    "INPUT_FILE_PLACEHOLDER": "Envie um arquivo de texto, PDF ou DOCX para extrair frases automaticamente.",
    "INPUT_TEXT_LABEL": "Frases para Análise (uma por linha)",
    "INPUT_TEXT_PLACER_EMPTY": "PLACER_EMPTY",
    "INPUT_TEXT_PLACEHOLDER_EMPTY": "Digite as frases aqui (uma por linha) ou envie um arquivo para preencher.",
    "INPUT_TEXT_PLACEHOLDER_LOADED": "Frases do arquivo carregadas. Edite se necessário.",
    "OUTPUT_RESULTS_LABEL": "Respostas Geradas",
    "OUTPUT_RESULTS_PLACEHOLDER_EMPTY": "Os resultados da análise aparecerão aqui.",
    "BUTTON_GENERATE_LABEL": "✨ Gerar Respostas",
    "NO_PHRASES_PROVIDED_MSG": "Nenhuma frase foi fornecida para processamento.",
    "NO_VALID_PHRASES_MSG": "Nenhuma frase válida encontrada após a limpeza."
}

# --- Funções de Processamento ---
def segmentar_texto_em_frases(texto: str) -> list[str]:
    """
    Segmenta um texto em frases utilizando múltiplos delimitadores de pontuação.
    Frases vazias ou apenas espaços são removidas.
    """
    if not texto:
        return []
    frases = re.split(r'(?<=[.!?])\s*|\n', texto.strip())
    frases_filtradas = [frase.strip() for frase in frases if frase.strip()]
    return frases_filtradas

# Importa processar_arquivo do utils.phrase_extractor
from utils.phrase_extractor import processar_arquivo

def carregar_arquivo_e_extrair_frases(arquivo_obj: gr.File) -> gr.Textbox:
    """
    Utiliza a função processar_arquivo de utils.phrase_extractor para ler o conteúdo
    do arquivo e extrair as frases, retornando-as como um bloco de texto para o Gradio.
    """
    if arquivo_obj is None:
        return gr.Textbox(value="", placeholder=INPUT_TEXT_PLACEHOLDER_EMPTY)

    try:
        # Chama a função unificada de processamento de arquivo que retorna uma lista de frases
        frases = processar_arquivo(arquivo_obj.name)
        
        texto_frases = "\n".join(frases)
        return gr.Textbox(value=texto_frases, placeholder=LABELS["INPUT_TEXT_PLACEHOLDER_LOADED"])
    except Exception as e:
        return gr.Textbox(value=f"Erro ao processar o arquivo: {e}", placeholder=LABELS["INPUT_TEXT_PLACER_EMPTY"])


def gerar_respostas_para_frases(texto_das_frases: str) -> tuple[gr.Textbox, gr.Tabs]:
    """
    Recebe um bloco de texto (frases separadas por nova linha) e o processa
    com a API RAG+LLM (`res_generate_API`) usando a estratégia de múltiplos contextos.
    Retorna o texto formatado das respostas e uma atualização para mudar para a aba de resultados.
    """
    if not texto_das_frases or not texto_das_frases.strip():
        return gr.Textbox(value=LABELS["NO_PHRASES_PROVIDED_MSG"], interactive=False), gr.Tabs()

    print(f"Processando o bloco de frases para geração de resposta: \"{texto_das_frases[:100]}...\"")

    # Chama a função unificada de geração de resposta, especificando a estratégia RAG
    # O LLM então usará os múltiplos contextos recuperados para gerar uma única resposta consolidada.
    resposta_consolidada = res_generate_API(
        frase_entrada=texto_das_frases,
        documentos=documentos,
        index=index,
        embedder=embedder,
        llm_choice='gemini', # ou 'ollama', conforme a necessidade
        rag_strategy='multiplo' # A chave para usar a busca por múltiplos contextos
    )
    
    # O resultado será uma única resposta do LLM baseada nos múltiplos contextos.
    resultado_final = f"--- Resposta Consolidada para as Frases Fornecidas ---\n{resposta_consolidada}\n"

    # Retorna o resultado para o campo de texto e instrui a mudança para a segunda aba
    return gr.Textbox(value=resultado_final, interactive=False), gr.Tabs(selected=1)


# --- Construção da Interface Gradio ---
with gr.Blocks(title=LABELS["APP_TITLE"]) as interface:
    gr.Markdown(f"# {LABELS["APP_TITLE"]}")
    gr.Markdown(LABELS["APP_DESCRIPTION"])

    with gr.Tabs() as tabs_component:
        with gr.TabItem(LABELS["TAB_INPUT_TITLE"], id=0):
            gr.Markdown("## 📝 Passo 1: Forneça as Frases")
            input_arquivo = gr.File(
                label=LABELS["INPUT_FILE_LABEL"],
                type="filepath",
                file_types=['.txt', '.pdf', '.docx']
            )
            input_frases_editavel = gr.Textbox(
                label=LABELS["INPUT_TEXT_LABEL"],
                placeholder=LABELS["INPUT_TEXT_PLACEHOLDER_EMPTY"],
                lines=10,
                interactive=True
            )

            input_arquivo.upload(
                fn=carregar_arquivo_e_extrair_frases,
                inputs=input_arquivo,
                outputs=input_frases_editavel
            )

            botao_gerar = gr.Button(LABELS["BUTTON_GENERATE_LABEL"])

        with gr.TabItem(LABELS["TAB_RESULTS_TITLE"], id=1):
            gr.Markdown("## 📊 Passo 2: Visualize os Resultados")
            output_resultados = gr.Textbox(
                label=LABELS["OUTPUT_RESULTS_LABEL"],
                lines=15,
                interactive=False,
                placeholder=LABELS["OUTPUT_RESULTS_PLACEHOLDER_EMPTY"]
            )

    botao_gerar.click(
        fn=gerar_respostas_para_frases,
        inputs=input_frases_editavel,
        outputs=[output_resultados, tabs_component]
    )

if __name__ == "__main__":
    interface.launch()