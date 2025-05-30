import gradio as gr
from pages.main import view as main_page
from pages.about import view as about_page
from pages.help import view as help_page

with gr.Blocks(theme=gr.themes.Soft()) as demo:    
    main_page.interface.render()
with demo.route("Ajuda", "help"):
    help_page.interface.render()
with demo.route("Sobre", "about"):
    about_page.interface.render()

# Utilizar gradio app.py para modo com reload
if __name__ == "__main__":
    print("Executando a aplicação...")
    demo.launch()