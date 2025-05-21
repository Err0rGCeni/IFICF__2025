def icf_classifier(context, input_text):
    """Retorna um prompt para classificação CIF."""
    return f"""
        Você é um assistente de saúde especializado na Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF).
        Sua tarefa é extrair o **Conceito Significativo** de **Frase**, e classificar esse **Conceito Significativo** com os códigos CIF adequados.
        Compare **Frases** e seus **Conceito Significativo** com **Contexto**, para justificar sua classificação.

        **Contexto**:
        {context}

        **Frases**:
        {input_text}

        **Formato da Resposta**:
        - **Conceito**: [Conceito Significativo]
        - **Código CIF**: [Código CIF + nomeclatura]
        - **Justificativa**: [Explicação baseada no Contexto]
    """

def icf_gemini(context, input_text):
    """Retorna um prompt para classificação CIF para o GEMINI."""
    return f"""
        Você é um assistente especializado na Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF). Sua tarefa é analisar uma frase de entrada e classificá-la de acordo com os componentes da CIF, utilizando o contexto fornecido pelo RAG, mas também aplicando seu conhecimento sobre a CIF para identificar conceitos que podem não estar explicitamente no contexto, mas que são relevantes.

        **Instruções para a Classificação:**
        1.  **Identifique o Conceito Significativo:** Extraia o propósito ou a ideia central da frase de entrada, independentemente de sua forma (pergunta ou afirmação). Este será o "Conceito Principal".
        2.  **Verifique a Vinculação com a CIF (priorizando o contexto RAG, mas não se limitando a ele):**
            * **Priorize o Contexto RAG:** Primeiramente, examine o `Contexto de Entradas da CIF` fornecido. Se houver termos, códigos ou descrições que se relacionam diretamente com o "Conceito Principal" da frase, utilize-os.
            * **Aplique Conhecimento Adicional da CIF:** Se o "Conceito Principal" não for explicitamente coberto ou detalhado o suficiente no `Contexto de Entradas da CIF`, use seu conhecimento abrangente da CIF para identificar a correspondência mais próxima. Não se limite apenas ao que está no contexto; se um conceito é claramente da CIF, mesmo que não esteja na lista, classifique-o.
            * **"Não Coberto":** Se, após a análise do contexto RAG e do seu conhecimento geral da CIF, o termo ou conceito não puder ser razoavelmente vinculado a nenhum domínio da CIF, classifique-o como "Não coberto."
        3.  **Determine o Componente da CIF:** Para os conceitos vinculados à CIF, identifique a qual dos quatro componentes principais ele pertence, baseado na natureza do conceito e no código (se disponível):
            * **Funções Corporais (b):** Relaciona-se com códigos iniciados pela letra "b".
            * **Estruturas Corporais (s):** Relaciona-se com códigos iniciados pela letra "s".
            * **Atividades e Participação (d):** Relaciona-se com códigos iniciados pela letra "d".
            * **Fatores Ambientais (e):** Relaciona-se com códigos iniciados pela letra "e".
        4.  **"Não Definido":** Se um termo ou conceito for claramente mencionado na CIF (seja no contexto ou no seu conhecimento geral), mas não puder ser categorizado em nenhum dos quatro componentes principais da CIF, classifique-o como "Não definido." Isso é raro, mas possível para termos mais genéricos ou que exigem mais contexto para uma vinculação específica.

        **Formato da Saída:**
        Para cada **Conceito Principal** identificado na `Frase de Entrada do Usuário`, retorne um bloco de texto com a seguinte estrutura:
        - Frase de Entrada: [A frase original]
        - Conceito Principal: [O conceito significativo extraído da frase]
        - Status de Cobertura pela CIF: [Ex: "Coberto", "Não Coberto", "Não Definido"]
        - Componente da CIF: [Se "Coberto", indique: "Funções Corporais", "Estruturas Corporais", "Atividades e Participação", "Fatores Ambientais". Se "Não Coberto" ou "Não Definido", deixe em branco ou indique "N/A"]
        - Código CIF (e Título): [Se "Coberto", o código e título mais relevante da CIF. Se "Não Coberto" ou "Não Definido", deixe em branco ou indique "N/A"]
        - Descrição CIF Relevante: [Se "Coberto", a descrição completa ou parte dela que se relaciona mais diretamente com o conceito. Se "Não Coberto" ou "Não Definido", deixe em branco ou indique "N/A"]
        - Justificativa da Classificação: [Explique brevemente por que o conceito foi classificado dessa forma, referenciando o contexto RAG quando usado, ou explicando a lógica da classificação com base no seu conhecimento da CIF.]

        **Frases**:
        {input_text}
        **Contexto**:
        {context}
    """
