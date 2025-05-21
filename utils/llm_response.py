import ollama
import faiss
import os
from google import genai
from sentence_transformers import SentenceTransformer
from utils.rag_retriever import buscar_contexto_completo, buscar_multiplos_contextos
from utils.prompts import icf_classifier, icf_gemini

# Carrega a chave de API do Gemini de variáveis de ambiente para segurança
# Certifique-se de que a variável de ambiente 'GEMINI_API_KEY' esteja definida no seu sistema.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("AVISO: A variável de ambiente 'GEMINI_API_KEY' não está definida. A API do Gemini pode não funcionar.")

def gerar_contexto_para_llm(frase_entrada: str, documentos: list, index: faiss.Index, embedder: SentenceTransformer, estrategia_busca: str = 'multiplo') -> str:
    """
    Gera um contexto relevante para a frase de entrada, utilizando o sistema RAG.

    Esta função permite escolher entre duas estratégias de busca de contexto:
    'completo': Busca os contextos mais relevantes para a pergunta inteira.
    'multiplo': Segmenta a pergunta em frases e busca múltiplos contextos, garantindo unicidade.

    Args:
        frase_entrada (str): A frase ou pergunta do usuário para a qual o contexto será gerado.
        documentos (list): Uma lista de strings, representando os documentos/textos de onde o contexto será recuperado.
        index (faiss.Index): O índice FAISS pré-construído para busca de similaridade nos embeddings dos documentos.
        embedder (SentenceTransformer): O modelo de embedding utilizado para converter texto em vetores.
        estrategia_busca (str, opcional): A estratégia de busca de contexto a ser utilizada.
                                          Pode ser 'completo' ou 'multiplo'. Padrão é 'multiplo'.

    Returns:
        str: Uma string contendo os contextos recuperados, unidos por quebras de linha.
             Retorna uma string vazia se nenhum contexto for encontrado ou se a estratégia for inválida.

    Raises:
        ValueError: Se a estratégia de busca fornecida for inválida.
    """
    contextos_com_distancia = []
    if estrategia_busca == 'completo':
        contextos_com_distancia = buscar_contexto_completo(frase_entrada, documentos, index, embedder, k=5) # k=5 como padrão para contexto completo
    elif estrategia_busca == 'multiplo':
        contextos_com_distancia = buscar_multiplos_contextos(frase_entrada, documentos, index, embedder, k_por_frase=3) # k_por_frase=3 para múltiplos
    else:
        raise ValueError(f"Estratégia de busca de contexto inválida: '{estrategia_busca}'. Use 'completo' ou 'multiplo'.")

    # Extrai apenas o texto dos documentos da lista de tuplas (índice, texto, distância)
    contexto_textos = [texto for _, texto, _ in contextos_com_distancia]
    contexto_str = "\n".join(contexto_textos)
    return contexto_str

def gerar_resposta_ollama(frase_entrada: str, contexto: str) -> str:
    """
    Gera uma resposta utilizando o modelo de linguagem Ollama localmente.

    Constrói um prompt detalhado com a frase de entrada do usuário e o contexto recuperado
    para guiar o modelo na geração de uma resposta informada sobre CIF.

    Args:
        frase_entrada (str): A frase ou pergunta original do usuário.
        contexto (str): Uma string contendo o contexto relevante recuperado do RAG.

    Returns:
        str: A resposta gerada pelo modelo Ollama.

    Raises:
        ollama.ResponseError: Se houver um erro na comunicação com o servidor Ollama.
        Exception: Para outros erros inesperados durante a geração da resposta.
    """
    # Prompt com instruções detalhadas sobre CIF
    prompt = icf_classifier(contexto, frase_entrada)
    print("\n--- Prompt Gerado para Ollama ---")
    print(prompt)
    print("--- Fim do Prompt Ollama ---")

    try:
        resposta = ollama.generate(model='gemma3:1b', prompt=prompt)
        return resposta.get('response', 'Nenhuma resposta gerada pelo Ollama.')
    except ollama.ResponseError as e:
        print(f"Erro de resposta do Ollama: {e}")
        return f"Desculpe, ocorreu um erro ao gerar a resposta com Ollama: {e}"
    except Exception as e:
        print(f"Erro inesperado ao gerar resposta com Ollama: {e}")
        return f"Desculpe, ocorreu um erro inesperado: {e}"

def gerar_resposta_gemini(frase_entrada: str, contexto: str) -> str:
    """
    Gera uma resposta utilizando a API do Google Gemini.

    Conecta-se à API do Gemini, constrói um prompt específico para o modelo
    e envia a requisição para obter uma resposta com base na frase do usuário e no contexto.

    Args:
        frase_entrada (str): A frase ou pergunta original do usuário.
        contexto (str): Uma string contendo o contexto relevante recuperado do RAG.

    Returns:
        str: A resposta gerada pelo modelo Gemini.

    Raises:
        google.api_core.exceptions.GoogleAPIError: Se houver um erro na comunicação com a API do Gemini.
        Exception: Para outros erros inesperados durante a geração da resposta.
    """
    if not GEMINI_API_KEY:
        return "Erro: Chave de API do Gemini não configurada. Por favor, defina a variável de ambiente 'GEMINI_API_KEY'."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Prompt com instruções detalhadas sobre CIF
        prompt_gemini = icf_gemini(contexto, frase_entrada)

        print("\n--- Prompt Gerado para Gemini ---")
        print(prompt_gemini)
        print("--- Fim do Prompt Gemini ---")

        # Configuração da requisição para o modelo Gemini
        model_name = "gemini-2.5-flash-preview-04-17" # Preferindo "flash" para velocidade e custo
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt_gemini,
        )
        
        # Retorna o texto da resposta
        return response.text
    except e:
        # Capture a exceção geral de API do Google.
        # Erros como autenticação (Unauthenticated), argumentos inválidos (InvalidArgument)
        # ou limites de taxa (ResourceExhausted) seriam subclasses de GoogleAPIError.
        print(f"Erro da API do Gemini: {e}. Verifique sua GEMINI_API_KEY e os detalhes do erro.")
        if "Authentication" in str(e) or "API key" in str(e):
            return "Erro de autenticação com a API do Gemini. Verifique sua chave de API e permissões."
        return f"Desculpe, ocorreu um erro na API do Gemini: {e}"
    except Exception as e:
        print(f"Erro inesperado ao gerar resposta com Gemini: {e}")
        return f"Desculpe, ocorreu um erro inesperado: {e}"

# Função unificada para gerar resposta, permitindo escolher o LLM
def res_generate_API(frase_entrada: str, documentos: list, index: faiss.Index, embedder: SentenceTransformer,
                     llm_choice: str = 'gemini', rag_strategy: str = 'multiplo') -> str:
    """
    Função principal para gerar uma resposta utilizando um LLM (Ollama ou Gemini),
    com base em um contexto recuperado via RAG.

    Args:
        frase_entrada (str): A frase ou pergunta original do usuário.
        documentos (list): Uma lista de strings, representando os documentos de onde o contexto será recuperado.
        index (faiss.Index): O índice FAISS pré-construído para busca de similaridade nos embeddings.
        embedder (SentenceTransformer): O modelo de embedding.
        llm_choice (str, optional): O LLM a ser utilizado ('ollama' ou 'gemini'). Padrão é 'gemini'.
        rag_strategy (str, optional): A estratégia de busca de contexto ('completo' ou 'multiplo'). Padrão é 'multiplo'.

    Returns:
        str: A resposta gerada pelo LLM.

    Raises:
        ValueError: Se a escolha do LLM for inválida.
    """
    # 1. Gerar o contexto
    try:
        contexto_recuperado = gerar_contexto_para_llm(frase_entrada, documentos, index, embedder, estrategia_busca=rag_strategy)
    except ValueError as e:
        return str(e) # Retorna a mensagem de erro da estratégia inválida
    except Exception as e:
        return f"Erro ao recuperar contexto: {e}"

    if not contexto_recuperado:
        return "Não foi possível encontrar contexto relevante para a sua pergunta. Por favor, reformule ou forneça mais detalhes."

    # 2. Gerar a resposta usando o LLM escolhido
    if llm_choice.lower() == 'ollama':
        return gerar_resposta_ollama(frase_entrada, contexto_recuperado)
    elif llm_choice.lower() == 'gemini':
        return gerar_resposta_gemini(frase_entrada, contexto_recuperado)
    else:
        return f"Erro: Escolha de LLM inválida ('{llm_choice}'). Opções válidas são 'ollama' ou 'gemini'."
