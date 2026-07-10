from collections import defaultdict
from datetime import date

import openai
from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import action

from .ai_exercise import generate_exercise
from .ai_motivation import generate_motivation
from .ai_supplement import generate_supplement
from .models import (
    Exercise, Program, ProgramDay, Category, Motivation, Supplement, User, OTPCode,
    Conversation, Message, WorkoutLog, WorkoutExerciseEntry, WorkoutSet, NutritionLog,
    UserProgram, UserProgramDay, UserProgramExercise,
)


def _generate_or_error(request, generate_fn, brief):
    """AI generatsiyasini bajaradi; xato bo'lsa messages.error qo'shib None qaytaradi."""
    try:
        return generate_fn(brief)
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
    return None


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
            data = _generate_or_error(request, generate_exercise, brief)
            if data is not None:
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
            'intro_text': "Mashq haqida qisqacha yozing — AI nomi, tavsifi, bajarish bosqichlari, "
                          "ishlaydigan mushaklar, keng tarqalgan xatolar va jihozlarni 3 tilda "
                          "(o'zbek, rus, ingliz) to'ldirib, tayyor formaga o'tkazadi. Rasm va videoni "
                          "o'sha formada o'zingiz qo'shasiz.",
            'placeholder': "Masalan: Shtanga bilan yotib siqish, ko'krak uchun, o'rta daraja, 8-12 marta",
        }
        return TemplateResponse(request, 'admin/ai_add.html', context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        prefill = request.session.pop('ai_exercise_prefill', None)
        if prefill:
            initial.update(prefill)
        return initial

class ProgramDayInline(StackedInline):
    # StackedInline — TabularInline emas — chunki filter_horizontal vidjeti
    # (mashq tanlash oynasi) keng va baland; tor jadval qatoriga sig'may,
    # hammasi chalkashib qolar edi. Har bir kun endi o'z alohida, keng
    # bo'lgan kartochkasida ko'rinadi.
    model = ProgramDay
    extra = 1
    tab = True
    collapsible = True
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

@admin.register(Motivation)
class MotivationAdmin(ModelAdmin):
    list_display = ('quote_en', 'author', 'created_at')
    actions_list = ('ai_add',)

    @action(description="🤖 AI bilan qo'shish", url_path="ai-add", permissions=["add"])
    def ai_add(self, request):
        brief = (request.POST.get('brief') or '').strip()
        if request.method == 'POST' and brief:
            data = _generate_or_error(request, generate_motivation, brief)
            if data is not None:
                request.session['ai_motivation_prefill'] = data
                messages.success(request, "AI tayyorladi — tekshirib saqlang.")
                return redirect(reverse('admin:api_motivation_add'))
        elif request.method == 'POST':
            messages.error(request, "Mavzu yozing yoki tayyor iqtibosni joylashtiring.")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': "AI bilan iqtibos qo'shish",
            'brief': brief,
            'intro_text': "Mavzu yozing (masalan: 'sabr haqida', 'kuch haqida') — AI original "
                          "motivatsion gap yozadi, 3 tilda. Yoki mavjud iqtibosni muallifi bilan "
                          "joylashtiring — AI uni aniq tarjima qiladi.",
            'placeholder': "Masalan: kuch va sabr haqida qisqa gap",
        }
        return TemplateResponse(request, 'admin/ai_add.html', context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        prefill = request.session.pop('ai_motivation_prefill', None)
        if prefill:
            initial.update(prefill)
        return initial

@admin.register(Supplement)
class SupplementAdmin(ModelAdmin):
    list_display = ('name_en', 'name_uz', 'name_ru')
    search_fields = ('name_en', 'name_uz', 'name_ru')
    actions_list = ('ai_add',)
    fieldsets = (
        ('Basic Info', {'fields': ('img',)}),
        ('English Content', {'fields': ('name_en', 'benefits_en', 'origin_en', 'dosage_en', 'timing_en', 'sources_en')}),
        ('Uzbek Content', {'fields': ('name_uz', 'benefits_uz', 'origin_uz', 'dosage_uz', 'timing_uz', 'sources_uz')}),
        ('Russian Content', {'fields': ('name_ru', 'benefits_ru', 'origin_ru', 'dosage_ru', 'timing_ru', 'sources_ru')}),
    )

    @action(description="🤖 AI bilan qo'shish", url_path="ai-add", permissions=["add"])
    def ai_add(self, request):
        brief = (request.POST.get('brief') or '').strip()
        if request.method == 'POST' and brief:
            data = _generate_or_error(request, generate_supplement, brief)
            if data is not None:
                request.session['ai_supplement_prefill'] = data
                messages.success(request, "AI ma'lumotlarni to'ldirdi — tekshirib, rasm qo'shib saqlang.")
                return redirect(reverse('admin:api_supplement_add'))
        elif request.method == 'POST':
            messages.error(request, "Qo'shimcha nomini yozing (masalan: protein, kreatin).")

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': "AI bilan qo'shimcha qo'shish",
            'brief': brief,
            'intro_text': "Sport qo'shimchasi nomini yozing (masalan: kreatin, protein, BCAA) — AI "
                          "foydasi, tarkibi, dozasi, qachon ichish kerakligi va manbalarini 3 tilda "
                          "to'ldiradi. Rasmni o'zingiz qo'shasiz.",
            'placeholder': "Masalan: Kreatin monogidrat",
        }
        return TemplateResponse(request, 'admin/ai_add.html', context)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        prefill = request.session.pop('ai_supplement_prefill', None)
        if prefill:
            initial.update(prefill)
        return initial

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
    """Standart Django jadval o'rniga — foydalanuvchi bo'yicha guruhlangan,
    keyin suhbatdosh va chat ko'rinishiga chuqurlashadigan maxsus sahifa
    (Bridgin admindagi Xabarlar bo'limi naqshiga o'xshab)."""

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

    def changelist_view(self, request, extra_context=None):
        user_id = request.GET.get('user_id')
        if user_id:
            return self._chat_view(request, user_id, request.GET.get('partner_id'))
        return self._user_list_view(request, (request.GET.get('q') or '').strip())

    def _user_list_view(self, request, q):
        conversations = list(Conversation.objects.all())
        messages_qs = list(Message.objects.order_by('-created_at'))

        # foydalanuvchi -> u ishtirok etgan suhbat id'lari
        user_conv_ids = defaultdict(set)
        for c in conversations:
            user_conv_ids[c.user1_id].add(c.pk)
            user_conv_ids[c.user2_id].add(c.pk)

        # suhbat id -> xabarlar (created_at bo'yicha kamayish tartibida, chunki
        # messages_qs shunday saralangan)
        messages_by_conv = defaultdict(list)
        for m in messages_qs:
            messages_by_conv[m.conversation_id].append(m)

        users = User.objects.filter(pk__in=user_conv_ids.keys())
        if q:
            users = users.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(sent_messages__content__icontains=q)).distinct()

        rows = []
        for user in users:
            conv_ids = user_conv_ids[user.pk]
            total_messages = sum(len(messages_by_conv[cid]) for cid in conv_ids)
            last_message = None
            for cid in conv_ids:
                msgs = messages_by_conv[cid]
                if msgs and (last_message is None or msgs[0].created_at > last_message.created_at):
                    last_message = msgs[0]
            rows.append({
                'user': user,
                'partner_count': len(conv_ids),
                'total_messages': total_messages,
                'last_message': last_message,
            })

        rows.sort(key=lambda r: r['last_message'].created_at if r['last_message'] else r['user'].date_joined, reverse=True)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Xabarlar',
            'rows': rows,
            'total_users': len(rows),
            'total_messages': len(messages_qs),
            'q': q,
        }
        return TemplateResponse(request, 'admin/message_list.html', context)

    def _chat_view(self, request, user_id, partner_id):
        user = get_object_or_404(User, pk=user_id)
        conversations = (
            Conversation.objects.filter(Q(user1=user) | Q(user2=user))
            .select_related('user1', 'user2')
            .order_by('-updated_at')
        )

        partners = []
        for conv in conversations:
            partner = conv.user2 if conv.user1_id == user.pk else conv.user1
            partners.append({
                'conversation': conv,
                'partner': partner,
                'last_message': conv.messages.order_by('-created_at').first(),
            })

        selected_partner = None
        days = []
        if partner_id:
            selected_partner = get_object_or_404(User, pk=partner_id)
            conv = Conversation.objects.filter(
                Q(user1=user, user2=selected_partner) | Q(user1=selected_partner, user2=user)
            ).first()
            if conv:
                thread = list(conv.messages.select_related('sender').order_by('created_at'))
                days_map = {}
                for m in thread:
                    day = m.created_at.date()
                    days_map.setdefault(day, []).append(m)
                days = [{'date': day, 'messages': msgs} for day, msgs in days_map.items()]

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Xabarlar',
            'viewed_user': user,
            'partners': partners,
            'selected_partner': selected_partner,
            'days': days,
        }
        return TemplateResponse(request, 'admin/message_chat.html', context)


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
    """Tekis jadval o'rniga — foydalanuvchi bo'yicha guruhlangan, ichiga
    kirilganda sessiya (kun) bo'yicha ko'rsatiladigan ko'rinish."""

    inlines = [WorkoutSetInline]

    def changelist_view(self, request, extra_context=None):
        user_id = request.GET.get('user_id')
        if user_id:
            return self._user_view(request, user_id)
        return self._user_list_view(request, (request.GET.get('q') or '').strip())

    def _user_list_view(self, request, q):
        entries = list(
            WorkoutExerciseEntry.objects
            .select_related('workout_log', 'workout_log__user')
            .order_by('-workout_log__date', '-workout_log__created_at')
        )

        user_entries = defaultdict(list)
        for e in entries:
            user_entries[e.workout_log.user_id].append(e)

        users = User.objects.filter(pk__in=user_entries.keys())
        if q:
            users = users.filter(Q(full_name__icontains=q) | Q(email__icontains=q))

        rows = []
        for user in users:
            u_entries = user_entries[user.pk]
            rows.append({
                'user': user,
                'entry_count': len(u_entries),
                'last_entry': u_entries[0] if u_entries else None,  # allaqachon -date bo'yicha saralangan
            })
        rows.sort(key=lambda r: r['last_entry'].workout_log.date if r['last_entry'] else date.min, reverse=True)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Mashq yozuvlari',
            'rows': rows,
            'total_users': len(rows),
            'total_entries': len(entries),
            'q': q,
        }
        return TemplateResponse(request, 'admin/workout_entry_list.html', context)

    def _user_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        logs = (
            WorkoutLog.objects.filter(user=user)
            .prefetch_related('exercises__sets')
            .order_by('-date', '-created_at')
        )
        sessions = [{'log': log, 'exercises': list(log.exercises.all())} for log in logs]

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Mashq yozuvlari',
            'viewed_user': user,
            'sessions': sessions,
        }
        return TemplateResponse(request, 'admin/workout_entry_user.html', context)

class UserProgramExerciseInline(TabularInline):
    model = UserProgramExercise
    extra = 0
    tab = True

class UserProgramDayInline(TabularInline):
    model = UserProgramDay
    extra = 0
    tab = True
    inlines = [UserProgramExerciseInline]  # har bir kun ichida mashqlar ham shu sahifada tahrirlanadi

@admin.register(UserProgram)
class UserProgramAdmin(ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email')
    inlines = [UserProgramDayInline]

@admin.register(NutritionLog)
class NutritionLogAdmin(ModelAdmin):
    """Foydalanuvchi bo'yicha guruhlangan, ichiga kirilganda kunlar bo'yicha
    ko'rsatiladigan ko'rinish (Mashq yozuvlari bilan bir xil naqsh)."""

    def changelist_view(self, request, extra_context=None):
        user_id = request.GET.get('user_id')
        if user_id:
            return self._user_view(request, user_id)
        return self._user_list_view(request, (request.GET.get('q') or '').strip())

    def _user_list_view(self, request, q):
        logs = list(NutritionLog.objects.order_by('-date', '-created_at'))

        user_logs = defaultdict(list)
        for entry in logs:
            user_logs[entry.user_id].append(entry)

        users = User.objects.filter(pk__in=user_logs.keys())
        if q:
            users = users.filter(Q(full_name__icontains=q) | Q(email__icontains=q))

        rows = []
        for user in users:
            u_logs = user_logs[user.pk]
            rows.append({
                'user': user,
                'entry_count': len(u_logs),
                'last_entry': u_logs[0] if u_logs else None,  # allaqachon -date bo'yicha saralangan
            })
        rows.sort(key=lambda r: r['last_entry'].date if r['last_entry'] else date.min, reverse=True)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Ovqatlanish kundaliklari',
            'rows': rows,
            'total_users': len(rows),
            'total_entries': len(logs),
            'q': q,
        }
        return TemplateResponse(request, 'admin/nutrition_log_list.html', context)

    def _user_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        entries = list(NutritionLog.objects.filter(user=user).order_by('-date', '-created_at'))

        days_map = {}
        for e in entries:
            days_map.setdefault(e.date, []).append(e)
        days = [{'date': d, 'entries': es} for d, es in days_map.items()]

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Ovqatlanish kundaliklari',
            'viewed_user': user,
            'days': days,
        }
        return TemplateResponse(request, 'admin/nutrition_log_user.html', context)
