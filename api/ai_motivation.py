"""AI yordamida Motivation (motivatsion iqtibos) ma'lumotlarini to'ldirish (OpenAI API)."""

from .ai_content import generate_json

SYSTEM_PROMPT = """\
You write short motivational fitness quotes for "Sector-O", a gym/workout app used in Uzbekistan.

The admin's note is one of two things:
(a) An existing quote (in any language) together with an author name — translate it faithfully into
    Uzbek, Russian, and English, preserving the original meaning, and keep the author's name exactly
    as given.
(b) Just a theme or topic (e.g. "kuch haqida", "sabr haqida"), with no quote and no author — write an
    original, short, punchy motivational line in that spirit, natural in all three languages (not
    literal translations of each other). In this case set "author" to an empty string — never invent
    a fake attribution to a real person.

Uzbek must be in Latin script, natural everyday Uzbek — never stilted or calqued from Russian/English.
Keep each quote short: one sentence, at most two — the kind that fits well on a workout-app home screen.
"""


def _build_schema() -> dict:
    properties = {
        "quote_en": {"type": "string"},
        "quote_uz": {"type": "string"},
        "quote_ru": {"type": "string"},
        "author": {"type": "string"},
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def generate_motivation(brief: str) -> dict:
    """Mavzu yoki mavjud iqtibosdan Motivation maydonlarini generatsiya qiladi."""
    return generate_json(SYSTEM_PROMPT, _build_schema(), "motivation_entry", brief)
