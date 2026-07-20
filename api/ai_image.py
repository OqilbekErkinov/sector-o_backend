"""AI yordamida mashq uchun muqova rasm generatsiya qilish (OpenAI gpt-image-2).

Sifat qasddan "medium" qilib qo'yilgan, "high" emas: real sinovda "high" sifat
10+ daqiqa davom etib, oxir-oqibat qayta urinishlardan keyin ham vaqti tugab
ishlamay qoldi (OpenAI'ning shu paytdagi holati). "medium" esa ~90-100
soniyada barqaror ishlaydi va sifati ham yetarlicha yaxshi. Baribir bu
funksiya har doim fon oqimida (background thread) chaqirilishi kerak,
to'g'ridan-to'g'ri HTTP so'rov ichida emas — aks holda server/proxy timeout
xatosi chiqadi (xuddi matn generatsiyasida bir marta bo'lganidek).
"""

import base64

from openai import OpenAI

MODEL = "gpt-image-2"


def generate_exercise_image_bytes(name: str, description: str) -> bytes:
    """Mashq nomi/tavsifi asosida bitta muqova rasm generatsiya qilib, PNG baytlarini qaytaradi."""
    prompt = (
        f'A clean, professional fitness photograph showing correct form for the exercise '
        f'"{name}". {description} Real gym setting, realistic human anatomy, clear '
        f'demonstration of proper technique, well-lit, no text or watermarks overlaid on '
        f'the image.'
    )
    client = OpenAI(timeout=300.0)
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="medium",
        n=1,
    )
    return base64.b64decode(response.data[0].b64_json)
