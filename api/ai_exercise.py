"""AI yordamida Exercise ma'lumotlarini to'ldirish (OpenAI API).

Admin qisqacha ma'lumot beradi (odatda o'zbekcha), AI qolgan barcha
maydonlarni 3 tilda (uz/ru/en) to'ldirib, Exercise modeliga mos JSON qaytaradi.
"""

import json

from openai import OpenAI

MODEL = "gpt-5.5"

SYSTEM_PROMPT = """\
You are a professional fitness content writer for "Sector-O", a gym/workout app used in Uzbekistan.
The admin will give you a short, informal note about an exercise (usually in Uzbek, sometimes Russian or English).
Your job is to produce a complete, accurate, trainer-grade exercise entry for the app's database.

Quality bar (non-negotiable):
- Content must be factually correct and biomechanically sound — what a certified strength coach would write.
  Never invent dubious claims or unsafe advice.
- Write all three language versions (Uzbek, Russian, English) as natural, fluent text a native-speaking
  trainer would write — NOT word-for-word machine translations of each other. Real gym vocabulary only.
- Uzbek must be in Latin script, natural everyday Uzbek (never stilted or calqued from Russian/English).

Field rules:
- name_*: short exercise name (e.g. "Bench Press" / "Yotib shtanga ko'tarish" / "Жим лёжа").
- description_*: 2-4 sentences explaining what the exercise is and what it's good for.
- instructions_*: 4-8 clear step-by-step execution steps (setup, movement, breathing, control).
- muscles_*: 2-5 muscle names worked by the exercise (primary first).
- mistakes_*: 3-5 common mistakes to avoid.
- equipment: short English equipment names matching existing data style, e.g. "Barbell", "Bench",
  "Dumbbells", "Cable Machine", "Pull-up Bar". Use ["None"] for bodyweight exercises.
- duration: like "10 min" or "15-20 min".
- recommended_sets: like "3-4 sets, 8-12 reps".
- difficulty: pick the most realistic level.
- category_slug: pick the category that best fits the exercise from the allowed list.
- If the admin's note already specifies something (difficulty, reps, category...), respect it.
"""

_STR = {"type": "string"}
_STR_LIST = {"type": "array", "items": {"type": "string"}}


def _build_schema(category_slugs: list[str]) -> dict:
    properties = {
        "name_en": _STR, "name_uz": _STR, "name_ru": _STR,
        "description_en": _STR, "description_uz": _STR, "description_ru": _STR,
        "instructions_en": _STR_LIST, "instructions_uz": _STR_LIST, "instructions_ru": _STR_LIST,
        "muscles_en": _STR_LIST, "muscles_uz": _STR_LIST, "muscles_ru": _STR_LIST,
        "mistakes_en": _STR_LIST, "mistakes_uz": _STR_LIST, "mistakes_ru": _STR_LIST,
        "equipment": _STR_LIST,
        "difficulty": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced"]},
        "duration": _STR,
        "recommended_sets": _STR,
    }
    if category_slugs:
        properties["category_slug"] = {"type": "string", "enum": category_slugs}
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def generate_exercise(brief: str) -> dict:
    """Qisqacha ma'lumotdan to'liq Exercise maydonlarini generatsiya qiladi.

    Qaytadi: Exercise maydon nomlariga mos dict (+ ixtiyoriy "category_slug").
    API xatolari openai.* exception'lari sifatida ko'tariladi.
    """
    from .models import Category

    category_slugs = list(Category.objects.values_list("slug", flat=True))

    client = OpenAI()  # OPENAI_API_KEY .env orqali o'qiladi
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": "high"},
        instructions=SYSTEM_PROMPT,
        input=brief,
        text={
            "format": {
                "type": "json_schema",
                "name": "exercise_entry",
                "schema": _build_schema(category_slugs),
                "strict": True,
            }
        },
    )

    text = response.output_text
    if not text:
        raise RuntimeError("AI javob qaytarmadi — qayta urinib ko'ring.")
    return json.loads(text)
