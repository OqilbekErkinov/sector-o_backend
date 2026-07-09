import openai
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from .ai_exercise import generate_exercise
from .models import (
    Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement, User, OTPCode,
    Conversation, Message, WorkoutLog, WorkoutExerciseEntry, WorkoutSet, NutritionLog,
    UserProgram, UserProgramDay, UserProgramExercise,
)

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Exercise)
class ExerciseAdmin(ModelAdmin):
    list_display = ('name_en', 'category', 'difficulty', 'duration', 'views')
    list_filter = ('category', 'difficulty')
    search_fields = ('name_en', 'name_uz', 'name_ru')
    readonly_fields = ('views',)
    actions_list = ('ai_add',)
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'difficulty', 'duration', 'recommended_sets', 'img', 'video', 'equipment', 'views')}),
        ('English Content', {'fields': ('name_en', 'description_en', 'instructions_en', 'muscles_en', 'mistakes_en')}),
        ('Uzbek Content', {'fields': ('name_uz', 'description_uz', 'instructions_uz', 'muscles_uz', 'mistakes_uz')}),
        ('Russian Content', {'fields': ('name_ru', 'description_ru', 'instructions_ru', 'muscles_ru', 'mistakes_ru')}),
    )

    @action(description="🤖 AI bilan qo'shish", url_path="ai-add", permissions=["add"])
    def ai_add(self, request):
        brief = (request.POST.get('brief') or '').strip()
        if request.method == 'POST' and brief:
            try:
                data = generate_exercise(brief)
            except openai.AuthenticationError:
                messages.error(request, "OPENAI_API_KEY noto'g'ri yoki kiritilmagan — backend/.env faylini tekshiring.")
            except openai.RateLimitError:
                messages.error(request, "So'rovlar limiti oshdi — bir daqiqadan so'ng qayta urinib ko'ring.")
            except openai.APIStatusError as exc:
                messages.error(request, f"OpenAI API xatosi ({exc.status_code}): {exc.message}")
            except openai.APIConnectionError:
                messages.error(request, "Internet aloqasida xato — qayta urinib ko'ring.")
            except Exception as exc:
                messages.error(request, f"Xato: {exc}")
            else:
                slug = data.pop('category_slug', None)
                category = Category.objects.filter(slug=slug).first() if slug else None
                if category:
                    data['category'] = category.pk
                request.session['ai_exercise_prefill'] = data
                messages.success(request, "AI ma'lumotlarni to'ldirdi — tekshirib, rasm/video qo'shib saqlang.")
                return redirect(reverse('admin:api_exercise_add'))
        elif request.method == 'POST':
            messages.error(request, "Mashq haqida qisqacha ma'lumot yozing.")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': "AI bilan mashq qo'shish",
            'brief': brief,
        }
        return TemplateResponse(request, 'admin/api/exercise/ai_add.html', context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        prefill = request.session.pop('ai_exercise_prefill', None)
        if prefill:
            initial.update(prefill)
        return initial

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
    list_display = ('name_en', 'name_uz', 'name_ru')
    search_fields = ('name_en', 'name_uz', 'name_ru')
    fieldsets = (
        ('Basic Info', {'fields': ('img',)}),
        ('English Content', {'fields': ('name_en', 'benefits_en', 'origin_en', 'dosage_en', 'timing_en', 'sources_en')}),
        ('Uzbek Content', {'fields': ('name_uz', 'benefits_uz', 'origin_uz', 'dosage_uz', 'timing_uz', 'sources_uz')}),
        ('Russian Content', {'fields': ('name_ru', 'benefits_ru', 'origin_ru', 'dosage_ru', 'timing_ru', 'sources_ru')}),
    )

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

class MessageInline(TabularInline):
    model = Message
    extra = 0
    tab = True
    readonly_fields = ('sender', 'content', 'is_read', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'updated_at', 'created_at')
    search_fields = ('user1__email', 'user2__email', 'user1__full_name', 'user2__full_name')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ('id', 'sender', 'get_receiver', 'content_snippet', 'is_read', 'created_at')
    search_fields = ('content', 'sender__email', 'sender__full_name')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('get_receiver', 'created_at')

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('sender', 'get_receiver', 'content', 'is_read', 'created_at')
        }),
        ('Tizim (Kerak emas)', {
            'fields': ('conversation',),
            'classes': ('collapse',)
        })
    )

    def get_receiver(self, obj):
        if not obj or not obj.conversation_id:
            return "-"
        return obj.conversation.user2 if obj.conversation.user1 == obj.sender else obj.conversation.user1
    get_receiver.short_description = "Qabul qiluvchi"

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Xabar matni'


class WorkoutSetInline(TabularInline):
    model = WorkoutSet
    extra = 0
    tab = True

class WorkoutExerciseEntryInline(TabularInline):
    model = WorkoutExerciseEntry
    extra = 0
    tab = True

@admin.register(WorkoutLog)
class WorkoutLogAdmin(ModelAdmin):
    list_display = ('user', 'date', 'created_at')
    list_filter = ('date',)
    search_fields = ('user__email', 'user__full_name')
    inlines = [WorkoutExerciseEntryInline]

@admin.register(WorkoutExerciseEntry)
class WorkoutExerciseEntryAdmin(ModelAdmin):
    list_display = ('name', 'workout_log', 'exercise', 'order')
    search_fields = ('name',)
    inlines = [WorkoutSetInline]

class UserProgramExerciseInline(TabularInline):
    model = UserProgramExercise
    extra = 0
    tab = True

class UserProgramDayInline(TabularInline):
    model = UserProgramDay
    extra = 0
    tab = True

@admin.register(UserProgram)
class UserProgramAdmin(ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email')
    inlines = [UserProgramDayInline]

@admin.register(UserProgramDay)
class UserProgramDayAdmin(ModelAdmin):
    list_display = ('name', 'program', 'order')
    search_fields = ('name',)
    inlines = [UserProgramExerciseInline]

@admin.register(NutritionLog)
class NutritionLogAdmin(ModelAdmin):
    list_display = ('user', 'date', 'name', 'calories', 'protein_g', 'carbs_g', 'fat_g')
    list_filter = ('date',)
    search_fields = ('user__email', 'user__full_name', 'name')
