import gradio as gr

font=gr.themes.GoogleFont('Montserrat'),

softCIF = gr.themes.Soft(
    primary_hue=gr.themes.Color(c100="#F7CDC9", c200="#F1A9A2", c300="#EB867B", c400="#E56556", c50="#FCEEED", c500="#D4291A", c600="#C02417", c700="#A91F14", c800="#991b1b", c900="#921A11", c950="#7B150E"),
    secondary_hue="teal",
    neutral_hue="slate",
    font=gr.themes.GoogleFont('Montserrat'),
    font_mono=gr.themes.GoogleFont('Fira Code')
).set(
    background_fill_primary='white',
    shadow_drop='rgba(0,0,0,0.05) 0px 1px 2px 0px',
    shadow_drop_lg='0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    shadow_spread='3px',
    block_background_fill='*background_fill_primary',
    block_border_width='1px',
    block_border_width_dark='1px',
    block_label_background_fill='*background_fill_primary',
    block_label_background_fill_dark='*background_fill_secondary',
    block_label_text_color='*neutral_500',
    block_label_text_color_dark='*neutral_200',
    block_label_margin='0',
    block_label_padding='*spacing_sm *spacing_lg',
    block_label_radius='calc(*radius_sm - 1px) 0 calc(*radius_sm - 1px) 0',
    block_label_text_size='*text_sm',
    block_label_text_weight='400',
    block_title_background_fill='none',
    block_title_background_fill_dark='none',
    block_title_text_color='*neutral_500',
    block_title_text_color_dark='*neutral_200',
    block_title_padding='0',
    block_title_radius='none',
    block_title_text_weight='400',
    panel_border_width='0',
    panel_border_width_dark='0',
    checkbox_background_color_selected='*color_accent',
    checkbox_background_color_selected_dark='*color_accent',
    checkbox_border_color='*neutral_300',
    checkbox_border_color_dark='*neutral_700',
    checkbox_border_color_focus='*color_accent',
    checkbox_border_color_focus_dark='*color_accent',
    checkbox_border_color_selected='*color_accent',
    checkbox_border_color_selected_dark='*color_accent',
    checkbox_border_width='*input_border_width',
    checkbox_shadow='*input_shadow',
    checkbox_label_background_fill_selected='*checkbox_label_background_fill',
    checkbox_label_background_fill_selected_dark='*checkbox_label_background_fill',
    checkbox_label_shadow='none',
    checkbox_label_text_color_selected='*checkbox_label_text_color',
    input_background_fill='*neutral_100',
    input_border_color='*border_color_primary',
    input_shadow='none',
    input_shadow_dark='none',
    input_shadow_focus='*input_shadow',
    input_shadow_focus_dark='*input_shadow',
    slider_color='*color_accent',
    slider_color_dark='*color_accent',
    button_primary_background_fill_hover='*primary_600',
    button_primary_background_fill_hover_dark='*primary_700',
    button_primary_shadow='none',
    button_primary_shadow_hover='*button_primary_shadow',
    button_primary_shadow_active='*button_primary_shadow',
    button_primary_shadow_dark='none',
    button_secondary_background_fill='*neutral_200',
    button_secondary_background_fill_hover='*neutral_300',
    button_secondary_background_fill_hover_dark='*neutral_700',
    button_secondary_text_color='black',
    button_secondary_shadow='*button_primary_shadow',
    button_secondary_shadow_hover='*button_secondary_shadow',
    button_secondary_shadow_active='*button_secondary_shadow',
    button_secondary_shadow_dark='*button_primary_shadow'
)
