import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironpulse_backend.settings')
django.setup()

from api.models import Exercise, Category
from django.utils.text import slugify

def migrate():
    # Load JSON files
    base_path = r'd:\IronPulse-frontend\frontend\i18n\locales'
    with open(os.path.join(base_path, 'uz.json'), 'r', encoding='utf-8') as f:
        uz = json.load(f).get('exercises', {})
    with open(os.path.join(base_path, 'ru.json'), 'r', encoding='utf-8') as f:
        ru = json.load(f).get('exercises', {})
    with open(os.path.join(base_path, 'en.json'), 'r', encoding='utf-8') as f:
        en = json.load(f).get('exercises', {})

    all_keys = set(uz.keys()) | set(ru.keys()) | set(en.keys())
    # Remove metadata keys if any
    all_keys.discard('detail')

    for slug in all_keys:
        data_uz = uz.get(slug, {})
        data_ru = ru.get(slug, {})
        data_en = en.get(slug, {})

        name_en = data_en.get('name', slug.replace('-', ' ').title())
        
        # Try to find existing exercise by slug or name
        exercise = Exercise.objects.filter(slug=slug).first()
        if not exercise:
            exercise = Exercise.objects.filter(name_en=name_en).first()
        
        if not exercise:
            print(f"Creating new exercise: {name_en}")
            exercise = Exercise(name_en=name_en, slug=slug)
        else:
            print(f"Updating exercise: {name_en}")

        # Update fields
        exercise.name_uz = data_uz.get('name', name_en)
        exercise.name_ru = data_ru.get('name', name_en)
        
        exercise.description_uz = data_uz.get('description', '')
        exercise.description_ru = data_ru.get('description', '')
        exercise.description_en = data_en.get('description', '')
        
        exercise.instructions_uz = data_uz.get('instructions', [])
        exercise.instructions_ru = data_ru.get('instructions', [])
        exercise.instructions_en = data_en.get('instructions', [])
        
        exercise.muscles_uz = data_uz.get('muscles', [])
        exercise.muscles_ru = data_ru.get('muscles', [])
        exercise.muscles_en = data_en.get('muscles', [])
        
        exercise.mistakes_uz = data_uz.get('mistakes', [])
        exercise.mistakes_ru = data_ru.get('mistakes', [])
        exercise.mistakes_en = data_en.get('mistakes', [])
        
        # Duration fallback
        if not exercise.duration:
            exercise.duration = data_en.get('sets', '3-4 sets')

        exercise.save()

    print("Migration finished successfully!")

if __name__ == '__main__':
    migrate()
