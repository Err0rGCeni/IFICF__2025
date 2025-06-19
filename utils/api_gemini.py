import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from utils.prompts import icf_gemini_prompt

# Carrega as variáveis de ambiente (se você usar .env)
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_ID = os.getenv('MODEL_ID')
CONTEXT_FIXED = ""
context_path = os.path.join(os.getcwd(), "RAG", "CIF_Lista.txt")

try:
    with open(context_path, 'r', encoding='utf-8') as f:
        CONTEXT_FIXED = f.read()
except FileNotFoundError:
    CONTEXT_FIXED = "Erro: Arquivo de contexto não encontrado."

print("Context: ", CONTEXT_FIXED[:100])

def api_generate(user_input: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)

    llm_config = types.GenerateContentConfig(
        response_mime_type='text/plain',
        seed=1,
        system_instruction=icf_gemini_prompt,
    )

    user_prompt_content = types.Content(
        role='user',
        parts=[
            types.Part.from_text(text=CONTEXT_FIXED),
            types.Part.from_text(text=user_input)
        ],
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_prompt_content,
        config=llm_config
    )

    return response.text

if __name__ == "__main__":
    test_string = "O paciente sente dores abdominais agudas, localizadas principalmente na região inferior do abdômen. Fadiga. Náuseas. Vômitos.  Diarreia. Dificuldade para respirar. Dor no peito. O paciente observa vermelhidão persistente na pele, acompanhada de coceira em áreas específicas. Eu não consigo enxergar objetos a longas distâncias, com visão embaçada ao tentar focar. Tontura ou perda de equilíbrio. O paciente apresenta fraqueza súbita em um lado do corpo, dificultando movimentos do braço e perna."
    print(f"Enviando...\n{test_string}")
    res = api_generate(test_string)
    print(res)