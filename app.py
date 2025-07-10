import gradio as gr
import os
from pages.theme import softCIF
from pages.main import view as main_page
from pages.about import view as about_page
from pages.feedback import view as feedback_page

with gr.Blocks(theme=softCIF) as demo:    
    main_page.interface.render()
with demo.route("Sobre", "about"):
    about_page.interface.render()
with demo.route("Contato", "feedback"):
    feedback_page.interface.render()

# Utilizar gradio app.py para modo com reload
# A linha abaixo garante que o Gradio use a porta fornecida pelo Cloud Run
# e que seja acessível de fora do contêiner.
if __name__ == "__main__":
    print("Executando a aplicação...")
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))