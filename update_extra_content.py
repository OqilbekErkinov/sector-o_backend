import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ironpulse_backend.settings')
django.setup()

from api.models import Exercise, Program, ProgramDay

def update_content():
    print("Updating videos and adding programs...")

    # 1. YouTube Video Links for Exercises
    video_links = {
        'bench-press': 'https://www.youtube.com/embed/rT7DgCrQWsk',
        'push-ups': 'https://www.youtube.com/embed/IODxDxX7oi4',
        'tricep-dips': 'https://www.youtube.com/embed/6kALZikcZd0',
        'pushdowns': 'https://www.youtube.com/embed/2-LAMcpzZRo',
        'pull-ups': 'https://www.youtube.com/embed/eGo4IYlbE5g',
        'deadlift': 'https://www.youtube.com/embed/op9kVnSso6Q',
        'bicep-curl': 'https://www.youtube.com/embed/ykJmrZ5v0Oo',
        'hammer-curl': 'https://www.youtube.com/embed/TwD-YGVP4Bk',
        'overhead-press': 'https://www.youtube.com/embed/2yjwxtZ_Vkg',
        'lateral-raises': 'https://www.youtube.com/embed/3VcKaXpzqRo',
        'squats': 'https://www.youtube.com/embed/ultWZbUMPL8',
        'lunges': 'https://www.youtube.com/embed/QOVaHwm-Q6U',
        'wrist-curls': 'https://www.youtube.com/embed/SshZHe9Cst0',
        'reverse-curls': 'https://www.youtube.com/embed/nRgxYX2Ve9w',
        'calf-raises': 'https://www.youtube.com/embed/GWL6vO_9_54',
        'seated-calf-raises': 'https://www.youtube.com/embed/JbyjN7BWZr8',
        'crunches': 'https://www.youtube.com/embed/Xyd_fa5zoEU',
        'plank': 'https://www.youtube.com/embed/pSHjTRCQxIw',
    }

    for slug, video_url in video_links.items():
        ex = Exercise.objects.filter(slug=slug).first()
        if ex:
            ex.video = video_url
            ex.save()
            print(f"Updated video for: {ex.name_en}")

    # 2. Create 2 High-Quality Programs
    # Program 1: Muscle Building Elite
    prog1, _ = Program.objects.get_or_create(name_en='Muscle Building Elite', defaults={
        'name_uz': 'Mushak o\'stirish (Elite)',
        'name_ru': 'Набор мышечной массы',
        'level': 'Advanced',
        'duration': '8 Hafta',
        'description_en': 'Professional program for maximum muscle hypertrophy.',
        'description_uz': 'Maksimal mushak o\'stirish uchun professional dastur.',
        'description_ru': 'Профессиональная программа для максимальной гипертрофии.',
    })

    # Program 2: Fat Burn Master
    prog2, _ = Program.objects.get_or_create(name_en='Fat Burn Master', defaults={
        'name_uz': 'Ozish sirlari (Master)',
        'name_ru': 'Мастер жиросжигания',
        'level': 'Beginner',
        'duration': '4 Hafta',
        'description_en': 'Burn fat and get shredded with high intensity training.',
        'description_uz': 'Yuqori intensivlikdagi mashqlar bilan yog\'larni yoqing.',
        'description_ru': 'Сжигайте жир и придите в форму с интенсивными тренировками.',
    })

    # 3. Add Days and Exercises to Programs
    # Day 1 for Muscle Building: Chest & Triceps
    d1, _ = ProgramDay.objects.get_or_create(program=prog1, name_en='Day 1: Chest & Triceps', defaults={
        'name_uz': '1-kun: Ko\'krak va Triceps',
        'name_ru': 'День 1: Грудь и Трицепс',
        'order': 1
    })
    d1.exercises.add(
        Exercise.objects.get(slug='bench-press'),
        Exercise.objects.get(slug='push-ups'),
        Exercise.objects.get(slug='tricep-dips'),
        Exercise.objects.get(slug='pushdowns')
    )

    # Day 1 for Fat Burn: Full Body & Cardio
    fd1, _ = ProgramDay.objects.get_or_create(program=prog2, name_en='Day 1: Full Body Blast', defaults={
        'name_uz': '1-kun: Butun tana mashqi',
        'name_ru': 'День 1: Все тело',
        'order': 1
    })
    fd1.exercises.add(
        Exercise.objects.get(slug='squats'),
        Exercise.objects.get(slug='push-ups'),
        Exercise.objects.get(slug='plank'),
        Exercise.objects.get(slug='crunches')
    )

    print("All content updated successfully!")

if __name__ == '__main__':
    update_content()
