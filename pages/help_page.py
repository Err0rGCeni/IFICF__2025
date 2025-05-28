import gradio as gr
import os

img1 = os.path.join(os.path.dirname(__file__), "../static/images/logo.jpeg")

# --- Constantes de Interface ---
LABELS = {
    "LANDING_TITLE": "#CIF LINK _ Versão 2.0",
    "BTN_START": "Começar",
    "BTN_ABOUT": "Saiba Mais"
}

ROUTES = {
    "MAIN": "/main",
    "ABOUT": "/about"
}


with gr.Blocks() as interface:
    gr.Image("static/images/logo.jpeg", height=100)
    gr.Markdown(LABELS["LANDING_TITLE"], elem_id="landing_title")
    with gr.Row():
        gr.Button(LABELS["BTN_START"], link=ROUTES["MAIN"], elem_id="btn_start")
        gr.Button(LABELS["BTN_ABOUT"], link=ROUTES["ABOUT"], elem_id="btn_about")

if __name__ == "__main__":
    interface.launch()