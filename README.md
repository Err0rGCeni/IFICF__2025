# ICF 2025: Pre-release

O CIF Link 2.0 é um projeto que visa amplificar a utilização da Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF) ao receber uma forma de texto, seja por arquivo .pdf ou texto digitado pelo usuário, extrair suas frases e conceitos significativos, e então relacionar cada contexto significativo a uma codificação mais adequada da CIF. 

Este projeto começou propondo-se a utilizar **FAISS** e **Ollama** para uma aplicação com LLM assistido por RAG; e **Gradio** para uma interface rápida e simples. Esta _branch_ possui código legado que pode ser útil para futura referência.

Por limitações de conhecimento técnico, _hardware_, tempo de entrega, e evolução de IAs no periodo de desenvolvimento, este projeto migrou para a utilização da estratégia CAG ao Gemini 2.5 via API.

## Requisitos

## Principais Dependências
- **Gradio**: Para criar a interface de usuário.
- **Plotly Express**: Para criação de gráficos referentes a análise da resposta do modelo.
  - **Kaleido**: Geração de imagens estáticas do Plotly
- **ReportLab**: Geração de arquivo pdf para relatório da vinculação realizada.
- **Google Gen AI SDK**: Lida com a utilização de APIs de IAs generativas do Google.
- **gspread**: API para Planilhas Google (Feedback)

## Instalação

1. Clonar este repositório:
   ```bash
   git clone https://github.com/Err0rGCeni/IFICF__2025
   cd IFICF__2025
   ```
2. Criar um ambiente virtual Python (Recomendável)
    ```bash
    python -m venv venv
    venv\Scripts\activate  # No Windows
    source venv/bin/activate  # No Linux/Mac
    ```
3. Instalar dependências: `pip install -r requirements.txt`

## Configuração e Utilização

1. Crie ou copie uma chave para utilização da API: [AI Studio](https://aistudio.google.com/app/apikey)
2. Crie um arquivo .env com sua chave: `GEMINI_API_KEY = A...z`
3. Para utilização do Feedback, seguir o guia em [gspread - Authentication](https://docs.gspread.org/en/v6.1.4/oauth2.html)
  - Isso levará à criação manual de `credentials/cif-link-v2-creds.json`, ou sua adaptação.
3. Confirme ou modifique os arquivos de Contexto/Conhecimento (CAG)
4. Executar o script principal: `python app.py`
5. Acessar a interface no navegador pelo link fornecido no terminal (geralmente `http://127.0.0.1:7860`)

## Estruturação

- `docs/`: Arquivos para documentação README.md (print, etc.).
- `pages/`: Códigos para as páginas do projeto  (Home, Main, About).
- `CIF/`: Contém a lista de códigos CIF (ListaCIF.pdf)
- `sandbox/`: Scripts isolados para testes e outras funcionalidades.
- `static/`: Arquivos de estilo e imagens.
- `utils/`: Códigos com lógicas específicas de funcionalidades.
- `app.py`: Código principal para aplicação com interface grádio simples.
