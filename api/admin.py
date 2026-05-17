from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Exercise, Program, ProgramDay, Category, Motivation, Diet, Supplement, User, OTPCode, Conversation, Message

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
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'difficulty', 'duration', 'recommended_sets', 'img', 'video', 'equipment', 'views')}),
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
