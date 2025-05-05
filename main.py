import ollama
import faiss
import gradio as gr
import numpy as np
import os

print("Inicializando...")
# Função para carregar e processar o conhecimento
def inicializar_rag():
    """Inicializa o modelo de embeddings, documentos e índice FAISS a partir dos arquivos especificados."""
    # Caminhos dos arquivos
    caminhos_arquivos = [
        r'.\RAG\B(BodyFunctions).txt',
        r'.\RAG\D(Activities&Participation).txt',
        r'.\RAG\E(Environmental).txt',
        r'.\RAG\S(BodyStructures).txt'
    ]
    
    documentos = []
    # Carrega e processa cada arquivo
    for caminho in caminhos_arquivos:
        if os.path.exists(caminho):            
            with open(caminho, 'r', encoding='utf-8') as f:
                # Divide em parágrafos (ou outro critério, se necessário)
                conteudo = f.read().split('\n\n')
                documentos.extend(conteudo)
        else:
            print(f"Arquivo não encontrado: {caminho}")
    
    if not documentos:
        raise ValueError("Nenhum documento foi carregado. Verifique os caminhos dos arquivos.")
    
    print(f"Trabalhando em {len(documentos)} documentos ...")
    # Gera embeddings usando o Ollama
    embeddings = []
    for index, doc in enumerate(documentos):
        if index % 250 == 0:
            print(f"{index} Embeddings...")
        # nomic-embed-text é um modelo para parágrafos mais longos
        response = ollama.embed(model="nomic-embed-text", input=doc)
        embeddings.append(response['embeddings'][0])  # Acessa o embedding gerado
    print(f"Trabalhando em {len(embeddings)} embeddings...")
    embeddings = np.array(embeddings, dtype=np.float32)  # Converte para numpy array
    
    # Cria o índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return documentos, index

# Função para buscar contexto relevante
def buscar_contexto(pergunta, documentos, index, k=5):
    """Busca os k documentos mais relevantes para a pergunta."""
    # Gera embedding para a pergunta usando o Ollama
    response = ollama.embed(model="nomic-embed-text", input=pergunta)
    query_embedding = np.array([response['embeddings'][0]], dtype=np.float32)
    
    # Busca no índice FAISS
    D, I = index.search(query_embedding, k)
    return [documentos[i] for i in I[0]]

# Função para gerar resposta com o Ollama
def gerar_resposta(frase_entrada, documentos, index):
    """Gera uma resposta baseada no contexto recuperado."""
    contexto = buscar_contexto(frase_entrada, documentos, index)
    contexto_str = "\n".join(contexto)
    
    # Prompt com instruções detalhadas sobre CIF
    prompt = f"""
        Sua tarefa é analisar a frase fornecida, identificar o conceito significativo e associar o(s) código(s) CIF mais adequado(s), utilizando o contexto no RAG para embasar sua decisão. Quando aplicável, forneça até duas classificações para o mesmo conceito, refletindo diferentes perspectivas.

        **Instruções para Codificação da Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF)**:
        - Códigos CIF são formados por: **componente** (uma letra) + **capítulo** (um número) + **níveis** (números adicionais, se aplicável). Exemplo: b280 (Funções Corporais, capítulo b2, nível 280 - Sensação de dor).
        - **Componentes**:
        - **b** (Funções Corporais): Refere-se a funções fisiológicas ou psicológicas (ex.: audição, dor, movimento).
        - Capítulos de **b**: Funções Mentais - b1; Funções Sensoriais e Dor - b2; Funções da Voz e Fala - b3; Funções dos sistemas cardiovascular, hematológico, imunológico e respiratório - b4; Funções dos sistemas digestivo, metabólico e endócrino - b5; Funções geniturinárias e reprodutivas - b6; Funções neuromusculoesqueléticas e relacionadas ao movimento - b7; Funções da pele e estruturas relacionadas - b8.
        - **s** (Estruturas Corporais): Refere-se a partes anatômicas (ex.: ouvido, braço).
        - Capítulos de **s**: Estruturas do sistema nervoso - s1; Olho, ouvido e estruturas relacionadas - s2; Estruturas relacionadas com a voz e a fala - s3; Estruturas do aparelho cardiovascular, do sistema imunológico e do aparelho respiratório - s4; Estruturas relacionadas com o aparelho digestivo e com os sistemas metabólico e endócrino - s5; Estruturas relacionadas com os aparelhos geniturinário e reprodutivo - s6; Estruturas relacionadas com o movimento - s7; Pele e estruturas relacionadas - s8.
        - **d** (Atividades e Participação): Refere-se a tarefas ou papéis sociais (ex.: caminhar, comunicar-se).
        - Capítulos de **d**: Aprendizagem e aplicação do conhecimento - d1; Tarefas e exigências gerais - d2; Comunicação - d3; Mobilidade - d4; Autocuidados - d5; Vida doméstica - d6; Interações e relacionamentos interpessoais - d7; Áreas principais da vida - d8; Vida comunitária, social e cívica - d9.
        - **e** (Fatores Ambientais): Refere-se a contextos externos (ex.: acessibilidade, suporte social).
        - Capítulos de **e**: Produtos e tecnologia - e1; Ambiente natural e mudanças ambientais feitas pelo homem - e2; Apoio e relacionamentos - e3; Atitudes - e4; Serviços, sistemas e políticas - e5.
        - **Detalhes de Capítulos e Níveis**: Consulte o RAG para informações sobre capítulos.
        - **Itens a Ignorar**: Não analise conceitos genéricos ou não relacionados à CIF, como nome, idade, gostos pessoais, ou outros dados irrelevantes para funcionalidade e incapacidade.

        **Tarefa**:
        1. Identifique o **conceito significativo** da frase, ou seja, o propósito ou a ideia central que ela expressa, independentemente de ser uma pergunta ou afirmação.
        2. Determine se o conceito pertence ao universo da CIF, verificando se ele descreve aspectos de funcionalidade, incapacidade ou fatores contextuais.
        3. Se pertencer à CIF:
        - Identifique o **componente** principal (b, s, d, ou e) que melhor reflete o conceito:
        - Consulte o RAG para vincular o conceito a uma **categoria de primeiro nível** e, somente se a frase fornecer detalhes específicos, a uma **categoria de segundo nível**.
        - **Múltiplas Perspectivas**: Avalie se o conceito pode ser classificado sob uma segunda perspectiva (ex.: um problema funcional **b** e uma limitação de atividade **d**). Se sim, forneça uma segunda classificação.
        4. Se o conceito não se encaixar em uma categoria específica da CIF:
        - Classifique como **'Não coberto' (NC)** (ex.: qualidade de vida → nc-qol) ou **'Não definido' (ND)** (ex.: saúde geral → nd-gh), utilizando o RAG.
        5. Forneça uma justificativa clara para cada código, com base no RAG.
        6. **Verificação Final**: Antes de finalizar, confirme se o código escolhido corresponde diretamente ao conceito significativo, comparando com as definições do RAG.

        **RAG**:
        {contexto_str}

        **Frase**:  
        {frase_entrada}

        **Formato da Resposta**:  
        - **Conceito**: [Descrição clara do conceito significativo]
        - **Classificação**:
        - **Código CIF**: [Código CIF + nomeclatura]
        - **Justificativa**: [Explicação baseada no RAG]
    """
    # modeel = gemma3:4b ou gemma3:1b etc.
    resposta = ollama.generate(model='gemma3:1b', prompt=prompt)
    return resposta['response']

# Função principal para a interface Gradio
def interface_rag(frase_entrada):
    """Função chamada pela interface Gradio."""
    resposta = gerar_resposta(frase_entrada, documentos, index)
    return resposta

# Inicialização do RAG
print("Inicializando RAG...")
documentos, index = inicializar_rag()

# Configuração da interface Gradio
interface = gr.Interface(
    fn=interface_rag,
    inputs=gr.Textbox(label="Digite sua frase", placeholder="Ex.: O que é função puberal?"),
    outputs=gr.Textbox(label="Resposta"),
    title="Sistema RAG para CIF",
    description="Pergunte algo sobre Funções Corporais, Estruturas Corporais, Atividades e Participação ou Fatores Ambientais com base na CIF."
)

# Iniciar a interface
print("Gerando Interface...")
#interface.launch(share=True) Quando modelo estiver no ar
interface.launch()