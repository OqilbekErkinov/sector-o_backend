"""YouTube Data API v3 orqali mashq uchun mos video qidirish.

Eslatma: AI modeliga to'g'ridan-to'g'ri "video link top" deb so'rash ishonchsiz —
model mavjud bo'lmagan linkni o'zidan to'qib chiqarishi mumkin. Shuning uchun
bu yerda haqiqiy YouTube qidiruvi ishlatiladi — admin natijalar orasidan
o'zi eng mosini tanlaydi.
"""

import os

import requests

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_exercise_videos(query: str, max_results: int = 6) -> list[dict]:
    """Berilgan so'rov bo'yicha YouTube'dan video nomzodlarini qidiradi.

    Qaytadi: [{"video_id", "title", "channel", "thumbnail", "url"}, ...]
    YOUTUBE_API_KEY topilmasa yoki so'rov muvaffaqiyatsiz bo'lsa, xato ko'taradi.
    """
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY .env faylida topilmadi.")

    response = requests.get(
        SEARCH_URL,
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "safeSearch": "strict",
            "videoEmbeddable": "true",
            "relevanceLanguage": "en",
            "key": api_key,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        snippet = item["snippet"]
        results.append({
            "video_id": video_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
    return results
