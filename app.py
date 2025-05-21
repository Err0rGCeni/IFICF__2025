import gradio as gr
from pages import landing_page, about_page, main_page

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    landing_page.landing.render()
with demo.route("Classificador", "main"):
    main_page.interface.render()
with demo.route("Sobre", "about"):
    about_page.about.render()

if __name__ == "__main__":
    print("Executando a aplicação...")
    demo.launch()