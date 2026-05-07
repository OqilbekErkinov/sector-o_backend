import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironpulse_backend.settings')
django.setup()

from api.models import Category, Program, Motivation, Diet, Supplement, Exercise

def seed():
    # 1. Categories
    categories = [
        {'name_uz': 'Kardiomashqlar', 'name_ru': 'Кардио', 'name_en': 'Cardio', 'slug': 'cardio'},
        {'name_uz': 'Kuch mashqlari', 'name_ru': 'Силовые', 'name_en': 'Strength', 'slug': 'strength'},
        {'name_uz': 'Yoga va cho\'zilish', 'name_ru': 'Йога и растяжка', 'name_en': 'Yoga & Stretching', 'slug': 'yoga'},
    ]
    for cat_data in categories:
        Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
    
    # 2. Programs
    if not Program.objects.exists():
        Program.objects.create(
            name_uz='Yangi boshlovchilar uchun',
            name_ru='Для начинающих',
            name_en='For Beginners',
            description_uz='30 kunlik bazaviy dastur',
            description_ru='30-дневная базовая программа',
            description_en='30-day basic program',
            duration='30 kun',
            level='Beginner'
        )

    # 3. Motivation
    if not Motivation.objects.exists():
        Motivation.objects.create(
            quote_uz='Bugungi harakat — ertangi natija',
            quote_ru='Сегодняшние усилия — завтрашний результат',
            quote_en='Today\'s effort is tomorrow\'s result',
            author='Sector-O',
        )

    # 4. Diet
    if not Diet.objects.exists():
        Diet.objects.create(
            meal_type='Breakfast',
            title_uz='Suli yormasi',
            title_ru='Овсянка',
            title_en='Oatmeal',
            description_uz='Mevalar va yong\'oqlar bilan',
            description_ru='С фруктами и орехами',
            description_en='With fruits and nuts'
        )

    # Link exercises to categories if they are not linked
    strength_cat = Category.objects.get(slug='strength')
    Exercise.objects.all().update(category=strength_cat)

    print("Seeding finished successfully!")

if __name__ == '__main__':
    seed()
