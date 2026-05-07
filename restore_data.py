import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironpulse_backend.settings')
django.setup()

from api.models import Category, Exercise, Program, Motivation, Diet, Supplement
from django.utils.text import slugify

def restore():
    print("Starting full data restoration...")

    # 1. Recreate Categories based on muscle groups found in media/categories
    muscle_groups = [
        {'slug': 'chest', 'name_en': 'Chest', 'name_ru': 'Грудь', 'name_uz': 'Ko\'krak', 'img': 'categories/chest.jpg'},
        {'slug': 'back', 'name_en': 'Back', 'name_ru': 'Спина', 'name_uz': 'Orqa', 'img': 'categories/back.jpg'},
        {'slug': 'shoulders', 'name_en': 'Shoulders', 'name_ru': 'Плечи', 'name_uz': 'Yelkalar', 'img': 'categories/shoulders.jpg'},
        {'slug': 'biceps', 'name_en': 'Biceps', 'name_ru': 'Бицепс', 'name_uz': 'Biceps', 'img': 'categories/biceps.jpg'},
        {'slug': 'triceps', 'name_en': 'Triceps', 'name_ru': 'Трицепс', 'name_uz': 'Triceps', 'img': 'categories/triceps.jpg'},
        {'slug': 'legs', 'name_en': 'Legs', 'name_ru': 'Ноги', 'name_uz': 'Oyoqlar', 'img': 'categories/legs.jpg'},
        {'slug': 'abs', 'name_en': 'Abs', 'name_ru': 'Пресс', 'name_uz': 'Press', 'img': 'categories/abs.jpg'},
        {'slug': 'forearms', 'name_en': 'Forearms', 'name_ru': 'Предплечья', 'name_uz': 'Bilaklar', 'img': 'categories/forearms.jpg'},
        {'slug': 'calf', 'name_en': 'Calf', 'name_ru': 'Икры', 'name_uz': 'Boldir', 'img': 'categories/calf.jpg'},
    ]

    cat_map = {}
    for cg in muscle_groups:
        cat, created = Category.objects.get_or_create(slug=cg['slug'], defaults={
            'name_en': cg['name_en'],
            'name_ru': cg['name_ru'],
            'name_uz': cg['name_uz'],
            'img': cg['img']
        })
        cat_map[cg['slug']] = cat
        if created: print(f"Created category: {cg['name_en']}")

    # 2. Update Exercises with Images and Link to Categories
    # Load i18n data to get muscle links
    base_path = r'd:\IronPulse-frontend\frontend\i18n\locales'
    with open(os.path.join(base_path, 'en.json'), 'r', encoding='utf-8') as f:
        en_data = json.load(f).get('exercises', {})

    for slug, data in en_data.items():
        if slug == 'detail': continue
        
        exercise = Exercise.objects.filter(slug=slug).first()
        if not exercise:
            exercise = Exercise(slug=slug, name_en=data.get('name', slug))
        
        # Link image
        img_path = f"exercises/{slug}.jpg"
        if os.path.exists(os.path.join('media', img_path)):
            exercise.img = img_path
        
        # Determine category based on muscles
        muscles = data.get('muscles', [])
        found_cat = None
        for m in muscles:
            m_lower = m.lower()
            if 'chest' in m_lower or 'ko\'krak' in m_lower: found_cat = cat_map.get('chest')
            elif 'back' in m_lower or 'orqa' in m_lower: found_cat = cat_map.get('back')
            elif 'shoulder' in m_lower or 'yelka' in m_lower: found_cat = cat_map.get('shoulders')
            elif 'bicep' in m_lower: found_cat = cat_map.get('biceps')
            elif 'tricep' in m_lower: found_cat = cat_map.get('triceps')
            elif 'leg' in m_lower or 'oyoq' in m_lower or 'quad' in m_lower or 'hamstring' in m_lower or 'glute' in m_lower: found_cat = cat_map.get('legs')
            elif 'abs' in m_lower or 'qorin' in m_lower or 'core' in m_lower: found_cat = cat_map.get('abs')
            elif 'forearm' in m_lower or 'bilak' in m_lower: found_cat = cat_map.get('forearms')
            elif 'calf' in m_lower or 'boldir' in m_lower: found_cat = cat_map.get('calf')
            
            if found_cat: break
        
        if found_cat:
            exercise.category = found_cat
            print(f"Linked {exercise.name_en} to {found_cat.name_en}")
        
        exercise.save()

    # 3. Add Diets
    if not Diet.objects.exists():
        Diet.objects.create(meal_type='Breakfast', title_en='High Protein Oatmeal', title_ru='Протеиновая овсянка', title_uz='Proteinli suli yormasi', icon='🥣', description_en='Oats with whey protein and berries.')
        Diet.objects.create(meal_type='Lunch', title_en='Chicken & Rice', title_ru='Курица с рисом', title_uz='Tovuq va guruch', icon='🍗', description_en='Grilled chicken breast with brown rice.')
        Diet.objects.create(meal_type='Dinner', title_en='Salmon & Veggies', title_ru='Лосось с овощами', title_uz='Losos va sabzavotlar', icon='🐟', description_en='Baked salmon with steamed broccoli.')

    # 4. Add Supplements
    if not Supplement.objects.exists():
        Supplement.objects.create(name_en='Whey Protein', name_ru='Сывороточный протеин', name_uz='Zardobli protein', benefits_en='Fast muscle recovery.')
        Supplement.objects.create(name_en='Creatine Monohydrate', name_ru='Креатин моногидрат', name_uz='Kreatin monogidrat', benefits_en='Increased strength and power.')

    print("Restoration finished successfully!")

if __name__ == '__main__':
    restore()
