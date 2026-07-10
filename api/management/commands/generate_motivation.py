"""AI yordamida yangi motivatsion iqtibos generatsiya qilib, bazaga qo'shadi.

Har kuni cron orqali ishga tushirish mo'ljallangan (masalan soat 09:00 da):

    0 9 * * * cd /path/to/backend && /path/to/venv/bin/python manage.py generate_motivation >> /var/log/sector_motivation.log 2>&1

Buyruq har safar ishga tushganda ham darhol yangi iqtibos qo'shavermaydi —
oxirgi qo'shilgan yozuvdan beri kamida 4 kun o'tganini tekshiradi, aks holda
hech narsa qilmay chiqib ketadi. Shu sababli uni har kuni ishga tushirsa ham
bo'ladi, taxminan har 4 kunda bittasi qo'shiladi.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.ai_motivation import generate_motivation
from api.models import Motivation

MIN_INTERVAL = timedelta(days=4)
RECENT_LOOKBACK = 15


class Command(BaseCommand):
    help = "AI yordamida yangi motivatsion iqtibos generatsiya qilib, bazaga qo'shadi (4 kunda bir marta)."

    def handle(self, *args, **options):
        last = Motivation.objects.order_by('-pk').first()
        if last and last.created_at and timezone.now() - last.created_at < MIN_INTERVAL:
            self.stdout.write("Hali vaqti kelmadi — o'tkazib yuborildi.")
            return

        recent_quotes = list(
            Motivation.objects.order_by('-pk').values_list('quote_uz', flat=True)[:RECENT_LOOKBACK]
        )
        avoid_note = ""
        if recent_quotes:
            avoid_note = (
                " Bu gaplar/mavzular allaqachon ishlatilgan, ularni va ularga juda o'xshashlarini "
                "takrorlama: " + "; ".join(q for q in recent_quotes if q)
            )

        brief = (
            "Sport zali ilovasi uchun original, kuchli motivatsion gap yoz — mashq, sabr, intizom, "
            "kuch, o'z-o'zini yengish, izchillik kabi mavzulardan birini tanlab. Muallif ko'rsatilmasin."
            + avoid_note
        )

        data = generate_motivation(brief)
        obj = Motivation.objects.create(**data)
        self.stdout.write(self.style.SUCCESS(f"Yaratildi (id={obj.pk}): {obj.quote_uz}"))
