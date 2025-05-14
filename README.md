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

1. Confirme ou modifique os arquivos de RAG:
2. Executar o script principal: `python main.py`
3. Acessar a interface no navegador pelo link fornecido no terminal (geralmente `http://127.0.0.1:7860`)

## Estruturação

- `docs/`: Arquivos para documentação README.md (print, etc.);
- `prompts/`: Pasta para _futuros_ prompts pré-formatados.
- `RAG/`: CIF segmentada e formatada, base de dados.
  - `data/`: Arquivos prontos para utilização no banco de dados.
- `tools/`: Arquivos para _futuras_ ferramentas e utilização de agentes.
- `utils/`: Arquivos para testes e/ou outras futuras funcionalidades.
  - `faiss_interface`: Interface Gráfica para testar Embeddings e recuperação do banco de dados.
  - `faiss_rag`: Código para criação, escrita e recuperação do banco de dados.

- `main.py`: Código principal para aplicação com interface grádio simples.
- `prompt_tester.py`: Código alternativo para aplicação com interface para manipulação do prompt e observação do contexto e resposta gerada.
