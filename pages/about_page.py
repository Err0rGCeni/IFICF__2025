import gradio as gr
import os

img1 = os.path.join(os.path.dirname(__file__), "../static/images/logo.jpeg")

with gr.Blocks() as about:
    gr.Markdown("## Sobre a Classificação Internacional de Funcionalidade, Incapacidade e Saúde (CIF)")
    gr.Markdown("A Classificação Internacional de Funcionalidade (CIF) é uma ferramenta de classificação da Organização Mundial da Saúde (OMS) que fornece uma estrutura para entender e descrever a funcionalidade e a incapacidade em diferentes contextos.")
    gr.Markdown("## Conceito Significativo: **Propósito da informação** a ser linkada. Qual a ideia central? Sobre o que é essa informação?")
    gr.Markdown("> O conceito significativo é o **propósito da informação** ou ideia central da frase. Cieza et al., 2016.")
    gr.Image(img1, height=200)

if __name__ == "__main__":
    about.launch()