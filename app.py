import gradio as gr
from pages.theme import softCIF
from pages.main import view as main_page
from pages.about import view as about_page
from pages.feedback import view as feedback_page

with gr.Blocks(theme=softCIF) as demo:    
    main_page.interface.render()
with demo.route("Ajuda", "help"):
    about_page.interface.render()
with demo.route("Contato", "feedback"):
    feedback_page.interface.render()

# Utilizar gradio app.py para modo com reload
if __name__ == "__main__":
    print("Executando a aplicação...")
    demo.launch()