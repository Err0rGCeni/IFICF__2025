# pages/main/tab01_input.py
import gradio as gr
from typing import Dict, Any
from .strings import STRINGS

def create_input_components() -> Dict[str, Any]:
    """
    Cria e retorna os componentes de entrada, onde um seletor de rádio
    controla a visibilidade de grupos distintos para upload de arquivo e
    entrada de texto, cada um com seu próprio botão.
    """
    
    input_type_radio = gr.Radio(
        ["Vinculação por documento 📙", "Vinculação manual ✍️"],
        label="Selecione o tipo de entrada",
        value="Vinculação por documento 📙"
    )

    # --- Grupo de Upload de Arquivo ---
    # Usando gr.Group para controlar a visibilidade do bloco.
    # visible=True porque é a opção padrão do Radio.
    with gr.Group(visible=True) as file_input_group:
        file_input = gr.File(
            label="Carregue o documento (PDF, TXT)",
            file_types=['.pdf', '.txt'],
        )
        button_process_file = gr.Button(
            value=STRINGS["BTN_PROCESS_FILE_LABEL"],
            interactive=False,
            variant="primary"
        )

    # --- Grupo de Entrada de Texto ---
    # Usando gr.Group com visible=False porque não é a opção padrão.
    with gr.Group(visible=False) as text_input_group:
        text_input = gr.Textbox(
            label="Insira o texto para análise",
            lines=8,
            placeholder="relato de dor persistente na articulação do joelho direito...",
        )
        button_process_text = gr.Button(
            value=STRINGS["BTN_PROCESS_TEXT_LABEL"],
            interactive=False,
            variant="primary"
        )

    def _switch_input_visibility(selection: str) -> Dict[gr.Group, Dict[str, bool]]:
        """Alterna a visibilidade dos grupos de entrada."""
        is_document_selected = "documento" in selection
        return {
            file_input_group: gr.update(visible=is_document_selected),
            text_input_group: gr.update(visible=not is_document_selected)
        }

    input_type_radio.change(
        fn=_switch_input_visibility,
        inputs=input_type_radio,
        outputs=[file_input_group, text_input_group]
    )

    # --- Lógica de habilitação dos botões ---
    
    def _update_file_button_state(file_obj: Any) -> gr.Button:
        """Habilita o botão de arquivo apenas se um arquivo for carregado."""
        return gr.update(interactive=file_obj is not None)

    def _update_text_button_state(text: str) -> gr.Button:
        """Habilita o botão de texto apenas se o texto tiver conteúdo."""
        return gr.update(interactive=bool(text and text.strip()))

    file_input.change(
        fn=_update_file_button_state,
        inputs=file_input,
        outputs=button_process_file
    )
    
    text_input.change(
        fn=_update_text_button_state,
        inputs=text_input,
        outputs=button_process_text
    )

    # Retornamos os componentes interativos que a view.py precisa manipular.
    # Os próprios grupos não precisam ser retornados, a menos que se queira manipulá-los.
    return {
        "input_type_radio": input_type_radio,
        "file_input": file_input,
        "text_input": text_input,
        "button_process_file": button_process_file,
        "button_process_text": button_process_text,
    }