# ICF 2025

Este projeto utiliza **FAISS**, **Ollama**, **Gradio** e **NumPy** para criação.

## Requisitos

- Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina, e Ollama (`ollama pull gemma3:1b`).

![print](./docs/AboutSystem.png)

- Para Gemma3:4, ter hardware próximo a:
  - 3,4GB de GPU disponível [(Gemma3)](https://ai.google.dev/gemma/docs/core?hl=pt-br);
  - 4GB de RAM disponível [(Ollama)](https://github.com/ollama/ollama);


## Principais Dependências
- **FAISS**: Para indexação e busca vetorial.
- **Ollama**: Para geração de embeddings e respostas.
- **Gradio**: Para criar a interface de usuário.
- **NumPy**: Para manipulação de arrays.
- **SentenceTransformer**: Para utilização do modelo de embeddings.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/Err0rGCeni/IFICF__2025
   cd IFICF__2025
   ```
2. (Opcional, futuramente implantado)
    ```bash
    python -m venv venv
    venv\Scripts\activate  # No Windows
    source venv/bin/activate  # No Linux/Mac
    ```
3. Instalar dependências: `pip install -r requirements.txt`

## Utilização

1. Crie ou copie uma chave para utilização da API: [AI Studio](https://aistudio.google.com/app/apikey)
2. Crie um arquivo .env com sua chave: `GEMINI_API_KEY = A...z`
3. Confirme ou modifique os arquivos de RAG:
4. Executar o script principal: `python app.py`
5. Acessar a interface no navegador pelo link fornecido no terminal (geralmente `http://127.0.0.1:7860`)

## Estruturação

- `docs/`: Arquivos para documentação README.md (print, etc.).
- `pages/`: Códigos para as páginas do projeto  (Home, Main, About).
- `RAG/`: CIF segmentada e formatada, base de dados.
  - `data/`: Arquivos prontos para utilização no banco de dados.
- `sandbox/`: Scripts isolados para testes e outras funcionalidades.
- `static/`: Arquivos de estilo e imagens.
- `tools/`: Arquivos para _futuras_ ferramentas e utilização de agentes.
- `utils/`: Arquivos com lógicas separadas para diversas funções..
- `app.py`: Código principal para aplicação com interface grádio simples.
