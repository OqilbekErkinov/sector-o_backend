import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from api.models import Exercise, Program, ProgramDay

class Command(BaseCommand):
    help = 'Seeds the database with exercises and programs'

    def handle(self, *args, **options):
        self.stdout.write("Starting seeding...")

        # EXERCISES DATA
        exercises_data = [
            { "id": "bench-press", "name": "Bench Press", "category": "Chest", "img": "https://images.unsplash.com/photo-1652363722856-214ce6a06a44?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/rT7DgcrQWQE", "difficulty": "Intermediate", "equipment": ["Barbell", "Bench"], "duration": "15 min" },
            { "id": "push-ups", "name": "Push Ups", "category": "Chest", "img": "https://images.unsplash.com/photo-1718633625616-e5f297177a26?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/IODxDxX7oi4", "difficulty": "Beginner", "equipment": ["None"], "duration": "10 min" },
            { "id": "tricep-dips", "name": "Tricep Dips", "category": "Triceps", "img": "https://images.unsplash.com/photo-1530822847156-5df684ec5ee1?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/2z8JmcrW-As", "difficulty": "Beginner", "equipment": ["Parallel Bars", "Bench"], "duration": "10 min" },
            { "id": "pushdowns", "name": "Pushdowns", "category": "Triceps", "img": "https://images.unsplash.com/photo-1734980339581-d46dced9adf5?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/2-LAMcpzHLU", "difficulty": "Beginner", "equipment": ["Cable Machine"], "duration": "10 min" },
            { "id": "pull-ups", "name": "Pull Ups", "category": "Back", "img": "https://images.unsplash.com/photo-1605296867424-35fc25c9212a?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/eGo4IYlbE5g", "difficulty": "Intermediate", "equipment": ["Pull-up Bar"], "duration": "15 min" },
            { "id": "deadlift", "name": "Deadlift", "category": "Back", "img": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/op9kVnSso6Q", "difficulty": "Advanced", "equipment": ["Barbell"], "duration": "20 min" },
            { "id": "bicep-curl", "name": "Bicep Curl", "category": "Biceps", "img": "https://images.unsplash.com/photo-1598268030450-7a476f602bf6?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/ykJmrZ5v0BA", "difficulty": "Beginner", "equipment": ["Dumbbells", "Barbell"], "duration": "10 min" },
            { "id": "hammer-curl", "name": "Hammer Curl", "category": "Biceps", "img": "https://images.unsplash.com/photo-1681040517791-aba993f05b2b?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/zC3nLlEvin4", "difficulty": "Beginner", "equipment": ["Dumbbells"], "duration": "10 min" },
            { "id": "overhead-press", "name": "Overhead Press", "category": "Shoulders", "img": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/8NIn4v_uT4Q", "difficulty": "Intermediate", "equipment": ["Barbell", "Dumbbells"], "duration": "15 min" },
            { "id": "lateral-raises", "name": "Lateral Raises", "category": "Shoulders", "img": "https://plus.unsplash.com/premium_photo-1664299567740-34e1081e8100?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/3VcKaXpzqRo", "difficulty": "Beginner", "equipment": ["Dumbbells"], "duration": "10 min" },
            { "id": "squats", "name": "Squats", "category": "Legs", "img": "https://images.unsplash.com/photo-1574680178050-55c6a6a96e0a?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/gcNh17Ckjgg", "difficulty": "Beginner", "equipment": ["None", "Barbell"], "duration": "15 min" },
            { "id": "lunges", "name": "Lunges", "category": "Legs", "img": "https://plus.unsplash.com/premium_photo-1663133854192-0f1efe797e00?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/D7KaRcUTQeE", "difficulty": "Beginner", "equipment": ["None", "Dumbbells"], "duration": "15 min" },
            { "id": "wrist-curls", "name": "Wrist Curls", "category": "Forearms", "img": "https://images.unsplash.com/photo-1688521010779-5a04998b6d1d?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/P69yosgsh2E", "difficulty": "Beginner", "equipment": ["Barbell", "Dumbbells"], "duration": "8 min" },
            { "id": "reverse-curls", "name": "Reverse Curls", "category": "Forearms", "img": "https://images.unsplash.com/photo-1598575522694-d55ada5e48f4?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/3Uv08R_NToM", "difficulty": "Beginner", "equipment": ["Barbell"], "duration": "8 min" },
            { "id": "calf-raises", "name": "Calf Raises", "category": "Calf", "img": "https://plus.unsplash.com/premium_photo-1679635697818-2cdd42cbc6e0?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/gwLzBJYoWl4", "difficulty": "Beginner", "equipment": ["None", "Step"], "duration": "10 min" },
            { "id": "seated-calf-raises", "name": "Seated Calf Raises", "category": "Calf", "img": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/JpI426W9674", "difficulty": "Beginner", "equipment": ["Machine"], "duration": "10 min" },
            { "id": "crunches", "name": "Crunches", "category": "ABS", "img": "https://plus.unsplash.com/premium_photo-1661402015634-ecd5baa1481b?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/Xyd_ZGVNRmI", "difficulty": "Beginner", "equipment": ["None"], "duration": "10 min" },
            { "id": "plank", "name": "Plank", "category": "ABS", "img": "https://plus.unsplash.com/premium_photo-1661382292534-fdf10be6a1ec?auto=format&fit=crop&w=600&q=60", "video": "https://www.youtube.com/embed/pSHjTRCQxIw", "difficulty": "Beginner", "equipment": ["None"], "duration": "5 min" },
        ]

        # PROGRAMS DATA
        programs_data = [
            {
                "id": "beginner-7day",
                "name": "Beginner Full Body",
                "level": "Beginner",
                "duration": "7 Days",
                "img": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=800&q=70",
                "description": "A perfect start for newcomers. Focuses on building a foundation using core compound movements.",
                "days": [
                    {"name": "Day 1: Upper Body Focus", "exercises": ["push-ups", "bench-press", "pull-ups", "overhead-press"], "order": 1},
                    {"name": "Day 3: Lower Body Focus", "exercises": ["squats", "lunges", "calf-raises", "plank"], "order": 3},
                    {"name": "Day 5: Full Body Blast", "exercises": ["bench-press", "deadlift", "bicep-curl", "crunches"], "order": 5},
                ]
            },
            {
                "id": "muscle-gain-split",
                "name": "Muscle Gain Split",
                "level": "Intermediate",
                "duration": "5 Days",
                "img": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&w=800&q=70",
                "description": "Designed for those with some experience looking to increase hypertrophy through isolated splits.",
                "days": [
                    {"name": "Day 1: Chest & Triceps", "exercises": ["bench-press", "push-ups", "tricep-dips", "pushdowns"], "order": 1},
                    {"name": "Day 2: Back & Biceps", "exercises": ["pull-ups", "deadlift", "bicep-curl", "hammer-curl"], "order": 2},
                    {"name": "Day 3: Shoulders & Abs", "exercises": ["overhead-press", "lateral-raises", "crunches", "plank"], "order": 3},
                ]
            }
        ]

        exercise_map = {}

        # 1. SEED EXERCISES
        for data in exercises_data:
            self.stdout.write(f"Seeding Exercise: {data['name']}")
            image_url = data.pop('img')
            old_id = data.pop('id')
            
            exercise, created = Exercise.objects.get_or_create(name=data['name'], defaults=data)
            
            if created and image_url:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        file_name = f"{old_id}.jpg"
                        exercise.img.save(file_name, ContentFile(response.content), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {exercise.name}: {e}"))
            
            exercise_map[old_id] = exercise

        # 2. SEED PROGRAMS
        for p_data in programs_data:
            self.stdout.write(f"Seeding Program: {p_data['name']}")
            days_data = p_data.pop('days')
            image_url = p_data.pop('img')
            old_id = p_data.pop('id')
            
            program, created = Program.objects.get_or_create(name=p_data['name'], defaults=p_data)
            
            if created and image_url:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        file_name = f"prog_{old_id}.jpg"
                        program.img.save(file_name, ContentFile(response.content), save=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {program.name}: {e}"))

            # SEED DAYS
            for d_data in days_data:
                exercises_ids = d_data.pop('exercises')
                day, d_created = ProgramDay.objects.get_or_create(
                    program=program, 
                    name=d_data['name'], 
                    defaults={'order': d_data['order']}
                )
                if d_created:
                    for ex_id in exercises_ids:
                        if ex_id in exercise_map:
                            day.exercises.add(exercise_map[ex_id])

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))
