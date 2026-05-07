from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement, User, OTPCode

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Exercise)
class ExerciseAdmin(ModelAdmin):
    list_display = ('name_en', 'category', 'difficulty', 'duration')
    list_filter = ('category', 'difficulty')
    search_fields = ('name_en', 'name_uz', 'name_ru')
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'difficulty', 'duration', 'img', 'video', 'equipment')}),
        ('English Content', {'fields': ('name_en', 'description_en', 'instructions_en', 'muscles_en', 'mistakes_en')}),
        ('Uzbek Content', {'fields': ('name_uz', 'description_uz', 'instructions_uz', 'muscles_uz', 'mistakes_uz')}),
        ('Russian Content', {'fields': ('name_ru', 'description_ru', 'instructions_ru', 'muscles_ru', 'mistakes_ru')}),
    )

class ProgramDayInline(TabularInline):
    model = ProgramDay
    extra = 1
    tab = True
    filter_horizontal = ('exercises',)

@admin.register(Program)
class ProgramAdmin(ModelAdmin):
    list_display = ('name_en', 'level', 'duration')
    inlines = [ProgramDayInline]
    fieldsets = (
        ('Basic Info', {'fields': ('level', 'duration', 'img')}),
        ('English Content', {'fields': ('name_en', 'description_en')}),
        ('Uzbek Content', {'fields': ('name_uz', 'description_uz')}),
        ('Russian Content', {'fields': ('name_ru', 'description_ru')}),
    )

@admin.register(ProgramDay)
class ProgramDayAdmin(ModelAdmin):
    list_display = ('name_en', 'program', 'order')
    list_filter = ('program',)
    filter_horizontal = ('exercises',)

@admin.register(Motivation)
class MotivationAdmin(ModelAdmin):
    list_display = ('quote_en', 'author')

@admin.register(Diet)
class DietAdmin(ModelAdmin):
    list_display = ('meal_type', 'title_en')
    list_filter = ('meal_type',)

@admin.register(Supplement)
class SupplementAdmin(ModelAdmin):
    list_display = ('name_en',)

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'full_name', 'phone')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

@admin.register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_used')
    search_fields = ('email', 'code')
    list_filter = ('is_used',)
