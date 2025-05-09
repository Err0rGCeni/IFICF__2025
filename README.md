# ICF 2025

Este projeto utiliza **FAISS**, **Ollama**, **Gradio** e **NumPy** para criar ---.

## Requisitos

- Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina, e Ollama (`ollama pull nomic-embed-text gemma3:1b`).

![print](./docs/AboutSystem.png)

- Para Gemma3:4, ter hardware próximo a:
  - 3,4GB de GPU disponível [(Gemma3)](https://ai.google.dev/gemma/docs/core?hl=pt-br);
  - 4GB de RAM disponível [(Ollama)](https://github.com/ollama/ollama);


## Dependências
- **FAISS**: Para indexação e busca vetorial.
- **Ollama**: Para geração de embeddings e respostas.
- **Gradio**: Para criar a interface de usuário.
- **NumPy**: Para manipulação de arrays.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/Err0rGCeni/IFICF__2025
   cd IFICF__2025
   ```
2. (Opcional)
    ```bash
    python -m venv venv
    venv\Scripts\activate  # No Windows
    source venv/bin/activate  # No Linux/Mac
    ```
3. Instalar dependências: `pip install -r reqs.txt`

## Utilização

1. Confirme ou modifique os arquivos de RAG: `B(BodyFunctions).txt, D(Activities&Participation).txt, E(Environmental).txt, S(BodyStructures).txt`
2. Executar o script principal: `python main.py`
3. Acessar a interface no navegador pelo link fornecido no terminal (geralmente `http://127.0.0.1:7860`)

## Estruturação

- `CAG/`: Versão OCR em único arquivo, base de dados;
- `RAG/`: Versão OCR segmentada, base de dados;
- `etc/`: Arquivos para testes e/ou outras futuras funcionalidades;
  - `test_context...py`: Scripts para testar o embedding/retriever RAG;
- `docs/`: Arquivos para documentação (print, etc.);