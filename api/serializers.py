from rest_framework import serializers
from .models import Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement

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
