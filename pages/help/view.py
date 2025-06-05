import gradio as gr
import os

img1 = os.path.join(os.getcwd(), "static", "images", "logo.jpg")
# --- Constantes de Interface ---
LABELS = {
    "MD_LANDING_TITLE": "# CIF Link 2.0",
    "BTN_START": "Começar",
    "BTN_ABOUT": "Saiba Mais"
}

ROUTES = {
    "MAIN": "/",
    "ABOUT": "/about"
}


with gr.Blocks() as interface:
    gr.Image(
        value=img1,
        height=100,
        elem_id="logo_img",
        placeholder="CIF Link Logo",
        container=False,
        show_label=False,
        show_download_button=False,
        )
    gr.Markdown(LABELS["MD_LANDING_TITLE"], elem_id="landing_title")
    with gr.Row():
        gr.Button(LABELS["BTN_START"], link=ROUTES["MAIN"], elem_id="btn_start")
        gr.Button(LABELS["BTN_ABOUT"], link=ROUTES["ABOUT"], elem_id="btn_about")

if __name__ == "__main__":
    interface.launch()