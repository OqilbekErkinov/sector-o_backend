"""Admin panel uchun OpenAI orqali strukturaviy (JSON) kontent generatsiya qiluvchi umumiy yordamchi.

ai_exercise.py, ai_supplement.py, ai_motivation.py — barchasi shu yerdagi
generate_json() funksiyasidan foydalanadi, faqat system prompt va schema farq qiladi.
"""

import json

from openai import OpenAI

MODEL = "gpt-5.5"


def generate_json(instructions: str, schema: dict, schema_name: str, brief: str) -> dict:
    """Berilgan system prompt va JSON schema asosida OpenAI'dan structured JSON javob oladi."""
    client = OpenAI()  # OPENAI_API_KEY .env orqali o'qiladi
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": "high"},
        instructions=instructions,
        input=brief,
        text={
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": schema,
                "strict": True,
            }
        },
    )

    text = response.output_text
    if not text:
        raise RuntimeError("AI javob qaytarmadi — qayta urinib ko'ring.")
    return json.loads(text)
