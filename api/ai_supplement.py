"""AI yordamida Supplement (sport qo'shimchalari) ma'lumotlarini to'ldirish (OpenAI API)."""

from .ai_content import generate_json

SYSTEM_PROMPT = """\
You are a knowledgeable sports-nutrition writer for "Sector-O", a gym/workout app used in Uzbekistan.
The admin gives you information about a supplement (protein, creatine, BCAA, etc.), usually in Uzbek,
sometimes Russian or English. Produce accurate content for the app's database.

Two input modes:
(a) Short brief — just a supplement name, or a name plus a couple of keywords. Write all the content
    yourself, in all three languages, from your own nutrition knowledge.
(b) Full write-up — the admin already wrote complete content for one or more fields (most often in
    Uzbek): benefits, origin, dosage, timing, sources. When this happens, DO NOT rewrite, shorten,
    "improve", or rephrase what they wrote — preserve their exact facts, numbers, and wording for that
    language almost verbatim (only fix obvious typos/grammar). Then translate that same content
    faithfully into the other two languages, keeping every fact and number identical. Only invent
    content for fields the admin's text does not cover, or for the languages you must still fill in.

Quality bar (non-negotiable):
- Content must be factually correct — no exaggerated or unproven claims. If evidence for a benefit is
  mixed or weak, say so briefly rather than overselling it.
- When writing from scratch (mode a), all three language versions should read as natural text a sports
  nutritionist would write — NOT word-for-word translations of each other.
- Uzbek must be in Latin script, natural everyday Uzbek (never stilted or calqued).

Field rules:
- name_*: the supplement's common name.
- benefits_*: 2-4 sentences on what it actually does / is used for.
- origin_*: 1-3 sentences on what it's made from or how it's produced (e.g. whey from milk, creatine as
  a synthesized compound).
- dosage_*: a realistic typical daily dosage (e.g. "3-5 g per day").
- timing_*: when it's best taken (e.g. "post-workout, within 30 minutes").
- sources_*: 2-4 example food/product sources where relevant, or a short note that it's a standalone
  synthetic supplement if there's no natural food source.
"""

_STR = {"type": "string"}
_FIELDS = ["name", "benefits", "origin", "dosage", "timing", "sources"]
_LANGS = ("en", "uz", "ru")


def _build_schema() -> dict:
    properties = {f"{field}_{lang}": _STR for field in _FIELDS for lang in _LANGS}
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def generate_supplement(brief: str) -> dict:
    """Qo'shimcha nomidan to'liq Supplement maydonlarini generatsiya qiladi."""
    return generate_json(SYSTEM_PROMPT, _build_schema(), "supplement_entry", brief)
