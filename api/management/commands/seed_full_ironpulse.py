import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from api.models import Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement

class Command(BaseCommand):
    help = 'Seeds the database with full multi-language data for IronPulse'

    def handle(self, *args, **options):
        self.stdout.write("Starting comprehensive seeding...")

        # 1. CATEGORIES
        categories_data = [
            {"slug": "chest", "name_en": "Chest", "name_uz": "Ko'krak", "name_ru": "Грудь", "img": "https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?auto=format&fit=crop&w=800&q=60"},
            {"slug": "triceps", "name_en": "Triceps", "name_uz": "Triceps", "name_ru": "Трицепс", "img": "https://images.unsplash.com/photo-1530822847156-5df684ec5ee1?auto=format&fit=crop&w=800&q=60"},
            {"slug": "back", "name_en": "Back", "name_uz": "Orqa", "name_ru": "Спина", "img": "https://images.unsplash.com/photo-1605296867424-35fc25c9212a?auto=format&fit=crop&w=800&q=60"},
            {"slug": "biceps", "name_en": "Biceps", "name_uz": "Biceps", "name_ru": "Бицепс", "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?auto=format&fit=crop&w=800&q=60"},
            {"slug": "shoulders", "name_en": "Shoulders", "name_uz": "Yelkalar", "name_ru": "Плечи", "img": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=800&q=60"},
            {"slug": "legs", "name_en": "Legs", "name_uz": "Oyoqlar", "name_ru": "Ноги", "img": "https://images.unsplash.com/photo-1574680178050-55c6a6a96e0a?auto=format&fit=crop&w=800&q=60"},
            {"slug": "forearms", "name_en": "Forearms", "name_uz": "Bilak", "name_ru": "Предплечья", "img": "https://images.unsplash.com/photo-1594381898411-846e7d193883?auto=format&fit=crop&w=800&q=60"},
            {"slug": "calf", "name_en": "Calf", "name_uz": "Boldir", "name_ru": "Икры", "img": "https://images.unsplash.com/photo-1591117207239-788bf8de6c3b?auto=format&fit=crop&w=800&q=60"},
            {"slug": "abs", "name_en": "ABS", "name_uz": "Press", "name_ru": "Пресс", "img": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=800&q=60"},
        ]

        category_map = {}
        for cdict in categories_data:
            img_url = cdict.pop('img')
            cat, created = Category.objects.get_or_create(slug=cdict['slug'], defaults=cdict)
            if created and img_url:
                try:
                    res = requests.get(img_url)
                    if res.status_code == 200:
                        cat.img.save(f"{cat.slug}.jpg", ContentFile(res.content), save=True)
                except: pass
            category_map[cat.slug] = cat

        # 2. EXERCISES
        exercises_raw = [
            ("bench-press", "chest", "Bench Press", "Bench Press", "Жим лежа", "Intermediate", "15 min", "https://images.unsplash.com/photo-1652363722856-214ce6a06a44?auto=format&fit=crop&w=600&q=60"),
            ("push-ups", "chest", "Push Ups", "Push Ups (Ojimaniya)", "Отжимания", "Beginner", "10 min", "https://images.unsplash.com/photo-1718633625616-e5f297177a26?auto=format&fit=crop&w=600&q=60"),
            ("tricep-dips", "triceps", "Tricep Dips", "Tricep Dips", "Отжимания на брусьях", "Beginner", "10 min", "https://images.unsplash.com/photo-1530822847156-5df684ec5ee1?auto=format&fit=crop&w=600&q=60"),
            ("pushdowns", "triceps", "Pushdowns", "Pushdowns", "Разгибания рук в блоке", "Beginner", "10 min", "https://images.unsplash.com/photo-1734980339581-d46dced9adf5?auto=format&fit=crop&w=600&q=60"),
            ("pull-ups", "back", "Pull Ups", "Pull Ups (Turnikda tortilish)", "Подтягивания", "Intermediate", "15 min", "https://images.unsplash.com/photo-1605296867424-35fc25c9212a?auto=format&fit=crop&w=600&q=60"),
            ("deadlift", "back", "Deadlift", "Deadlift", "Становая тяга", "Advanced", "20 min", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=600&q=60"),
            ("bicep-curl", "biceps", "Bicep Curl", "Bicep Curl", "Подъем на бицепс", "Beginner", "10 min", "https://images.unsplash.com/photo-1598268030450-7a476f602bf6?auto=format&fit=crop&w=600&q=60"),
            ("hammer-curl", "biceps", "Hammer Curl", "Hammer Curl", "Молотковые сгибания", "Beginner", "10 min", "https://images.unsplash.com/photo-1681040517791-aba993f05b2b?auto=format&fit=crop&w=600&q=60"),
            ("overhead-press", "shoulders", "Overhead Press", "Overhead Press", "Армейский жим", "Intermediate", "15 min", "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=600&q=60"),
            ("lateral-raises", "shoulders", "Lateral Raises", "Lateral Raises", "Махи гантелями в стороны", "Beginner", "10 min", "https://plus.unsplash.com/premium_photo-1664299567740-34e1081e8100?auto=format&fit=crop&w=600&q=60"),
            ("squats", "legs", "Squats", "Squats (O'tirib turish)", "Приседания", "Beginner", "15 min", "https://images.unsplash.com/photo-1574680178050-55c6a6a96e0a?auto=format&fit=crop&w=600&q=60"),
            ("lunges", "legs", "Lunges", "Lunges (Siltanish)", "Выпады", "Beginner", "15 min", "https://plus.unsplash.com/premium_photo-1663133854192-0f1efe797e00?auto=format&fit=crop&w=600&q=60"),
            ("wrist-curls", "forearms", "Wrist Curls", "Wrist Curls", "Сгибания кистей", "Beginner", "8 min", "https://images.unsplash.com/photo-1688521010779-5a04998b6d1d?auto=format&fit=crop&w=600&q=60"),
            ("reverse-curls", "forearms", "Reverse Curls", "Reverse Curls", "Обратные сгибания", "Beginner", "8 min", "https://images.unsplash.com/photo-1598575522694-d55ada5e48f4?auto=format&fit=crop&w=600&q=60"),
            ("calf-raises", "calf", "Calf Raises", "Calf Raises", "Подьемы на носки", "Beginner", "10 min", "https://plus.unsplash.com/premium_photo-1679635697818-2cdd42cbc6e0?auto=format&fit=crop&w=600&q=60"),
            ("seated-calf-raises", "calf", "Seated Calf Raises", "Seated Calf Raises", "Подъемы на носки сидя", "Beginner", "10 min", "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=600&q=60"),
            ("crunches", "abs", "Crunches", "Crunches (Press)", "Скручивания", "Beginner", "10 min", "https://plus.unsplash.com/premium_photo-1661402015634-ecd5baa1481b?auto=format&fit=crop&w=600&q=60"),
            ("plank", "abs", "Plank", "Plank", "Планка", "Beginner", "5 min", "https://plus.unsplash.com/premium_photo-1661382292534-fdf10be6a1ec?auto=format&fit=crop&w=600&q=60"),
        ]

        exercise_map = {}
        for eid, cslug, name_en, name_uz, name_ru, diff, dur, img_url in exercises_raw:
            self.stdout.write(f"Seeding Exercise: {name_en}")
            ex, created = Exercise.objects.get_or_create(
                name_en=name_en,
                defaults={
                    "category": category_map[cslug],
                    "name_uz": name_uz,
                    "name_ru": name_ru,
                    "difficulty": diff,
                    "duration": dur,
                    "video": f"https://www.youtube.com/embed/sample_{eid}"
                }
            )
            if created and img_url:
                try:
                    res = requests.get(img_url)
                    if res.status_code == 200:
                        ex.img.save(f"{eid}.jpg", ContentFile(res.content), save=True)
                except: pass
            exercise_map[eid] = ex

        # 3. MOTIVATION
        Motivation.objects.create(
            quote_en="Success starts with self-discipline.",
            quote_uz="Muvaffaqiyat o'z-o'zini tarbiyalashdan boshlanadi.",
            quote_ru="Успех начинается с самодисциплины."
        )

        # 4. DIET
        Diet.objects.create(
            meal_type="Breakfast", icon="🍳",
            title_en="Breakfast", title_uz="Nonushta", title_ru="Завтрак",
            description_en="High-fiber oats with berries and eggs for protein.",
            description_uz="Suli yormasi (ovsyanka), rezavorlar va tuxum.",
            description_ru="Овсянка с ягодами и яйца для белка."
        )
        Diet.objects.create(
            meal_type="Lunch", icon="🍗",
            title_en="Lunch", title_uz="Tushlik", title_ru="Обед",
            description_en="Lean chicken breast with brown rice and leafy greens.",
            description_uz="Tovuq filesi, jigarrang guruch va sabzavotlar.",
            description_ru="Куриная грудка с бурым рисом и овощами."
        )
        Diet.objects.create(
            meal_type="Dinner", icon="🐟",
            title_en="Dinner", title_uz="Kechki ovqat", title_ru="Ужин",
            description_en="Grilled salmon or fish with steamed vegetables.",
            description_uz="Baliq, salat va foydali yog'lar.",
            description_ru="Гриль с лососем или рыбой и овощами на пару."
        )

        # 5. SUPPLEMENTS
        Supplement.objects.create(
            name_en="Whey Protein", name_uz="Whey Protein", name_ru="Whey Protein",
            benefits_en="Muscle repair and growth.",
            benefits_uz="Mushaklarni tiklash va o'stirish.",
            benefits_ru="Восстановление и рост мышц."
        )
        Supplement.objects.create(
            name_en="Creatine Monohydrate", name_uz="Kreatin monogidrat", name_ru="Креатин моногидрат",
            benefits_en="Increased strength and muscle volume.",
            benefits_uz="Kuch va mushak hajmini oshirish.",
            benefits_ru="Увеличение силы и объема мышц."
        )

        # 6. PROGRAMS (Simple link)
        p1, _ = Program.objects.get_or_create(name_en="7-Day Beginner Program", defaults={"name_uz": "7 kunlik yangi boshlovchilar uchun dastur", "name_ru": "7-дневная программа для новичков", "level": "Beginner", "duration": "7 Days"})
        ProgramDay.objects.create(program=p1, name_en="Day 1: Upper Body", name_uz="1-kun: Yuqori tana", name_ru="День 1: Верх тела", order=1).exercises.set([exercise_map['push-ups'], exercise_map['bench-press']])

        self.stdout.write(self.style.SUCCESS("Comprehensive seeding completed!"))
