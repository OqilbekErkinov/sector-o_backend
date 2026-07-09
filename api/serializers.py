from rest_framework import serializers
from .models import (
    Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement,
    WorkoutLog, WorkoutExerciseEntry, WorkoutSet, NutritionLog,
    UserProgram, UserProgramDay, UserProgramExercise,
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    category_name_uz = serializers.CharField(source='category.name_uz', read_only=True)
    category_name_en = serializers.CharField(source='category.name_en', read_only=True)
    category_name_ru = serializers.CharField(source='category.name_ru', read_only=True)

    class Meta:
        model = Exercise
        fields = '__all__'

class ProgramDaySerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = ProgramDay
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    days = ProgramDaySerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = '__all__'

class MotivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motivation
        fields = '__all__'

class DietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = '__all__'

class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = '__all__'


class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = ['id', 'set_number', 'weight_kg', 'reps']


class WorkoutExerciseEntrySerializer(serializers.ModelSerializer):
    sets = WorkoutSetSerializer(many=True)
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), required=False, allow_null=True
    )
    muscle_group = serializers.ChoiceField(choices=WorkoutExerciseEntry.MUSCLE_GROUP_CHOICES)

    class Meta:
        model = WorkoutExerciseEntry
        fields = ['id', 'exercise', 'name', 'muscle_group', 'order', 'sets']


class WorkoutLogSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseEntrySerializer(many=True)
    program_day = serializers.PrimaryKeyRelatedField(
        queryset=UserProgramDay.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = WorkoutLog
        fields = ['id', 'date', 'notes', 'program_day', 'exercises', 'created_at']
        read_only_fields = ['created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope program_day choices to the requesting user's own programs —
        # otherwise any authenticated user could tag their log with (and
        # thereby read the existence/name of) another user's program day.
        request = self.context.get('request')
        if request is not None:
            self.fields['program_day'].queryset = UserProgramDay.objects.filter(program__user=request.user)

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises')
        workout_log = WorkoutLog.objects.create(**validated_data)
        self._replace_exercises(workout_log, exercises_data)
        return workout_log

    def update(self, instance, validated_data):
        exercises_data = validated_data.pop('exercises', None)
        instance.date = validated_data.get('date', instance.date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        if exercises_data is not None:
            # Simplest correct approach for a small, whole-day log: replace
            # the exercise/set tree wholesale rather than diffing it.
            instance.exercises.all().delete()
            self._replace_exercises(instance, exercises_data)
        return instance

    def _replace_exercises(self, workout_log, exercises_data):
        for idx, exercise_data in enumerate(exercises_data):
            sets_data = exercise_data.pop('sets', [])
            exercise_data.setdefault('order', idx)
            entry = WorkoutExerciseEntry.objects.create(workout_log=workout_log, **exercise_data)
            for set_idx, set_data in enumerate(sets_data):
                set_data.setdefault('set_number', set_idx + 1)
                WorkoutSet.objects.create(exercise_entry=entry, **set_data)


class NutritionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionLog
        fields = ['id', 'date', 'meal_type', 'name', 'calories', 'protein_g', 'carbs_g', 'fat_g', 'created_at']
        read_only_fields = ['created_at']


class UserProgramExerciseSerializer(serializers.ModelSerializer):
    # Writable (not the ModelSerializer default read-only `id`) so an update
    # can tell "this is the same exercise slot, just edited" from "this is a
    # brand new one" — see UserProgramSerializer._sync_days.
    id = serializers.IntegerField(required=False)
    exercise = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), required=False, allow_null=True
    )
    # Unlike a real logged set, a program template exercise may not have a
    # muscle group chosen yet (e.g. right after copying from the catalog) —
    # the user fills it in the first time they see it, so it's optional here.
    muscle_group = serializers.ChoiceField(
        choices=WorkoutExerciseEntry.MUSCLE_GROUP_CHOICES, required=False, allow_blank=True
    )

    class Meta:
        model = UserProgramExercise
        fields = ['id', 'exercise', 'name', 'muscle_group', 'order']


class UserProgramDaySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    exercises = UserProgramExerciseSerializer(many=True)

    class Meta:
        model = UserProgramDay
        fields = ['id', 'name', 'order', 'exercises']


class UserProgramSerializer(serializers.ModelSerializer):
    days = UserProgramDaySerializer(many=True)

    class Meta:
        model = UserProgram
        fields = ['id', 'name', 'is_active', 'created_at', 'days']
        read_only_fields = ['is_active', 'created_at']

    def create(self, validated_data):
        days_data = validated_data.pop('days')
        program = UserProgram.objects.create(**validated_data)
        for idx, day_data in enumerate(days_data):
            day_data.pop('id', None)  # brand new program — any client-sent ids are meaningless
            self._create_day(program, day_data, idx)
        return program

    def update(self, instance, validated_data):
        days_data = validated_data.pop('days', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if days_data is not None:
            self._sync_days(instance, days_data)
        return instance

    def _create_day(self, program, day_data, order):
        exercises_data = day_data.pop('exercises', [])
        day_data['order'] = order
        day = UserProgramDay.objects.create(program=program, **day_data)
        for ex_idx, exercise_data in enumerate(exercises_data):
            exercise_data.pop('id', None)
            exercise_data['order'] = ex_idx
            UserProgramExercise.objects.create(day=day, **exercise_data)

    def _sync_days(self, program, days_data):
        """Updates days/exercises **in place** by id instead of deleting and
        recreating everything, so a WorkoutLog.program_day pointing at an
        edited-but-not-removed day keeps working — a rename or an added
        exercise must never silently disconnect a day from its history."""
        existing_days = {d.id: d for d in program.days.all()}
        kept_day_ids = set()

        for idx, day_data in enumerate(days_data):
            day_id = day_data.pop('id', None)
            exercises_data = day_data.pop('exercises', [])
            day_data['order'] = idx

            if day_id in existing_days:
                day = existing_days[day_id]
                day.name = day_data.get('name', day.name)
                day.order = day_data['order']
                day.save()
            else:
                day = UserProgramDay.objects.create(program=program, **day_data)

            kept_day_ids.add(day.id)
            self._sync_exercises(day, exercises_data)

        for day_id, day in existing_days.items():
            if day_id not in kept_day_ids:
                day.delete()

    def _sync_exercises(self, day, exercises_data):
        existing = {e.id: e for e in day.exercises.all()}
        kept_ids = set()

        for idx, exercise_data in enumerate(exercises_data):
            ex_id = exercise_data.pop('id', None)
            exercise_data['order'] = idx

            if ex_id in existing:
                exercise = existing[ex_id]
                for field, value in exercise_data.items():
                    setattr(exercise, field, value)
                exercise.save()
            else:
                exercise = UserProgramExercise.objects.create(day=day, **exercise_data)

            kept_ids.add(exercise.id)

        for ex_id, exercise in existing.items():
            if ex_id not in kept_ids:
                exercise.delete()
