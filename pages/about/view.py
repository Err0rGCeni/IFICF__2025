import gradio as gr
import os

from .strings import STRINGS

img1 = os.path.join(os.getcwd(), "static", "images", "logo.jpg")


with gr.Blocks() as interface:
    gr.Image(
    value=img1,
    height=200,
    elem_id="logo_img",
    placeholder="CIF Link Logo",
    container=False,
    show_label=False,
    show_download_button=False,
    )

    gr.Markdown(STRINGS["ABOUT_TITLE"], elem_id="about_title")

    gr.Markdown(STRINGS["SECTION_CIFLINK"])
    gr.Markdown(STRINGS["SECTION_CIFLINK_P1"])
    gr.Markdown(STRINGS["SECTION_CIFLINK_P2"])

    gr.Markdown(STRINGS["SECTION_CIFWHO"])
    gr.Markdown(STRINGS["SECTION_CIFWHO_P1"])
    gr.Markdown(STRINGS["SECTION_CIFWHO_LIST"])

    gr.Markdown(STRINGS["SECTION_CONCEPT"])
    gr.Markdown(STRINGS["SECTION_CONCEPT_P1"])
    gr.Markdown(STRINGS["SECTION_CONCEPT_REF"])

    gr.Markdown(STRINGS["SECTION_REFERENCES"])
    gr.Markdown(STRINGS["SECTION_REFERENCES_LINKS"])
    gr.Markdown(STRINGS["SECTION_REFERENCES_LIST"])
 
if __name__ == "__main__":
    interface.launch()