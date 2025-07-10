# utils/

Este diretório centraliza módulos com funcionalidades auxiliares e reutilizáveis que dão suporte à lógica principal do projeto. A organização visa separar as responsabilidades em subdiretórios coesos.

## Conteúdo

-   **`/apis`**: Contém os scripts responsáveis pela comunicação com APIs externas.
    -   `gemini.py`: Gerencia as chamadas para a API do Google Gemini, incluindo a formatação da entrada e o tratamento da resposta.
    -   `gsheets.py`: Abstrai a lógica de conexão e escrita de dados em planilhas do Google Sheets.

-   **`/report`**: Agrupa todos os módulos necessários para o processamento de dados e a geração do relatório final em PDF.
    -   `icf_categories.py`: Define as categorias da Classificação Internacional de Funcionalidade (CIF) através de uma `Enum`, centralizando códigos, rótulos e cores.
    -   `dataframe_creation.py`: Processa a resposta textual do modelo de linguagem para extrair e estruturar os dados em DataFrames do Pandas.
    -   `graph_creation.py`: Utiliza os DataFrames para criar os gráficos (pizza, barras e treemap) com a biblioteca Plotly.
    -   `pdf_creation.py`: Monta o arquivo PDF final, organizando o texto, as tabelas e os gráficos gerados.
    -   `report_creation.py`: Orquestra todo o fluxo de geração de relatório, chamando as funções dos outros módulos na ordem correta.

-   **`prompts.py`**: Armazena as instruções (prompts) detalhadas e estruturadas que são enviadas para o modelo de linguagem.