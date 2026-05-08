from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Exercise, Program, Category, Motivation, Diet, Supplement, User
from .serializers import (
    ExerciseSerializer, ProgramSerializer, CategorySerializer,
    MotivationSerializer, DietSerializer, SupplementSerializer
)


def landing_view(request):
    """Sector-O Backend Landing Page"""
    context = {
        'total_users': User.objects.count(),
        'total_exercises': Exercise.objects.count(),
        'total_programs': Program.objects.count(),
    }
    return render(request, 'landing.html', context)



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Exercise.objects.all()
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

class MotivationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Motivation.objects.all()
    serializer_class = MotivationSerializer
    permission_classes = [AllowAny]

class DietViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Diet.objects.all()
    serializer_class = DietSerializer
    permission_classes = [AllowAny]

class SupplementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplement.objects.all()
    serializer_class = SupplementSerializer
    permission_classes = [AllowAny]
