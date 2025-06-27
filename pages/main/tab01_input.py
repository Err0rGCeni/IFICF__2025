# pages/main/tab01_input.py
import gradio as gr
from typing import Dict, Any

def create_input_tabs() -> Dict[str, Any]:
    """
    Cria e retorna um bloco de entrada com um seletor de rádio para alternar
    entre o upload de arquivos e a inserção de texto. Retorna um dicionário
    de todos os seus componentes interativos.
    """
    
    # Seletor de rádio para escolher o tipo de entrada
    input_type_radio = gr.Radio(
        ["Vinculação de documento 📙", "Vinculação de texto ✍️"],
        label="Selecione o tipo de entrada",
        value=""  # Valor inicial padrão
    )

    # Componente de upload de arquivo, visível por padrão
    file_input = gr.File(
        label="Carregue o documento (PDF, TXT)",
        file_types=['.pdf', '.txt'],
        visible=False 
    )
    
    # Componente de caixa de texto, oculto por padrão
    text_input = gr.Textbox(
        label="Insira o texto para análise",
        lines=8,
        placeholder="relato de dor persistente na articulação do joelho direito, dores de cabeça...",
        visible=False
    )

    def switch_input_visibility(selection: str) -> Dict[gr.File, Dict[str, bool]]:
        """
        Altera a visibilidade dos componentes de entrada com base na seleção do rádio.
        
        Args:
            selection: O valor selecionado no gr.Radio.

        Returns:
            Um dicionário de atualizações para os componentes gr.File e gr.Textbox.
        """
        if "documento" in selection:
            # Mostra o input de arquivo, esconde o de texto
            return {
                file_input: gr.update(visible=True),
                text_input: gr.update(visible=False)
            }
        else:
            # Esconde o input de arquivo, mostra o de texto
            return {
                file_input: gr.update(visible=False),
                text_input: gr.update(visible=True)
            }

    # Associa a função de callback ao evento de mudança do seletor de rádio
    input_type_radio.change(
        fn=switch_input_visibility,
        inputs=input_type_radio,
        outputs=[file_input, text_input]
    )

    # Dicionário contendo todos os componentes que a view principal precisa para a lógica.
    # Os componentes de abas e botões de troca foram removidos.
    components = {
        "input_type_radio": input_type_radio,
        "file_input": file_input,
        "text_input": text_input,
    }
    
    return components