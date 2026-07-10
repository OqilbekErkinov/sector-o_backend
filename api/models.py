from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.text import slugify
import secrets, string

# ───── Custom User ─────
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email majburiy')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    full_name = models.CharField(max_length=150, blank=True, default='')
    is_active = models.BooleanField(default=False)  # Emailni tasdiqlagunga qadar False
    is_staff = models.BooleanField(default=False)
    img = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Gamification & Goals
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    weekly_goal = models.PositiveIntegerField(default=4)
    
    # Workout Stats
    workouts_done = models.PositiveIntegerField(default=0)
    active_days = models.PositiveIntegerField(default=0)
    current_week_workouts = models.PositiveIntegerField(default=0)
    last_workout_date = models.DateField(null=True, blank=True)

    # Nutrition goals — 0 means "not set", in which case the UI shows raw
    # totals only and skips any %-of-goal display.
    goal_calories = models.PositiveIntegerField(default=0)
    goal_protein_g = models.FloatField(default=0)
    goal_carbs_g = models.FloatField(default=0)
    goal_fat_g = models.FloatField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

# ───── OTP Code ─────
def generate_otp():
    return ''.join(secrets.choice(string.digits) for _ in range(6))

class OTPCode(models.Model):
    PURPOSE_CHOICES = [
        ('verify', 'Email verification'),
        ('reset', 'Password reset'),
        ('change_email', 'Email change'),
    ]
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6, default=generate_otp)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='verify')
    # Only used for purpose='change_email': the new email address pending confirmation
    new_email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # 10 daqiqa ichida amal qiladi
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} — {self.code}"

class Category(models.Model):
    name_uz = models.CharField(max_length=100, default='', blank=True)
    name_ru = models.CharField(max_length=100, default='', blank=True)
    name_en = models.CharField(max_length=100, default='')
    img = models.ImageField(upload_to='categories/', blank=True, null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name_en

class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    category = models.ForeignKey(Category, related_name='exercises', on_delete=models.SET_NULL, null=True, blank=True)
    
    name_uz = models.CharField(max_length=255, default='', blank=True)
    name_ru = models.CharField(max_length=255, default='', blank=True)
    name_en = models.CharField(max_length=255, default='')
    
    slug = models.SlugField(unique=True, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    duration = models.CharField(max_length=50, default='')
    img = models.ImageField(upload_to='exercises/', blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True)
    
    description_uz = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')
    
    instructions_uz = models.JSONField(default=list, blank=True)
    instructions_ru = models.JSONField(default=list, blank=True)
    instructions_en = models.JSONField(default=list, blank=True)
    
    muscles_uz = models.JSONField(default=list, blank=True)
    muscles_ru = models.JSONField(default=list, blank=True)
    muscles_en = models.JSONField(default=list, blank=True)
    
    mistakes_uz = models.JSONField(default=list, blank=True)
    mistakes_ru = models.JSONField(default=list, blank=True)
    mistakes_en = models.JSONField(default=list, blank=True)
    
    equipment = models.JSONField(default=list, blank=True)
    views = models.PositiveIntegerField(default=0)
    recommended_sets = models.CharField(max_length=100, default='3-4 sets, 8-12 reps', blank=True)
    

    def save(self, *args, **kwargs):
        if not self.slug and self.name_en:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en

class Program(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    name_uz = models.CharField(max_length=255, default='', blank=True)
    name_ru = models.CharField(max_length=255, default='', blank=True)
    name_en = models.CharField(max_length=255, default='')
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    duration = models.CharField(max_length=100, default='')
    img = models.ImageField(upload_to='programs/', blank=True, null=True)
    
    description_uz = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name_en

class ProgramDay(models.Model):
    program = models.ForeignKey(Program, related_name='days', on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=255, default='', blank=True)
    name_ru = models.CharField(max_length=255, default='', blank=True)
    name_en = models.CharField(max_length=255, default='', blank=True)
    
    exercises = models.ManyToManyField(Exercise, related_name='program_days', blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.program.name_en} - {self.name_en}"

class Motivation(models.Model):
    quote_uz = models.TextField(default='', blank=True)
    quote_ru = models.TextField(default='', blank=True)
    quote_en = models.TextField(default='')
    author = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.quote_en[:50]

class Diet(models.Model):
    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default='Breakfast')
    icon = models.CharField(max_length=10, default='🍳')
    
    title_uz = models.CharField(max_length=255, default='', blank=True)
    title_ru = models.CharField(max_length=255, default='', blank=True)
    title_en = models.CharField(max_length=255, default='')
    
    description_uz = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.meal_type}: {self.title_en}"

class Supplement(models.Model):
    name_uz = models.CharField(max_length=255, default='', blank=True)
    name_ru = models.CharField(max_length=255, default='', blank=True)
    name_en = models.CharField(max_length=255, default='')
    
    benefits_uz = models.TextField(blank=True, default='')
    benefits_ru = models.TextField(blank=True, default='')
    benefits_en = models.TextField(blank=True, default='')

    origin_uz = models.TextField(blank=True, default='')
    origin_ru = models.TextField(blank=True, default='')
    origin_en = models.TextField(blank=True, default='')
    
    dosage_uz = models.TextField(blank=True, default='')
    dosage_ru = models.TextField(blank=True, default='')
    dosage_en = models.TextField(blank=True, default='')
    
    timing_uz = models.TextField(blank=True, default='')
    timing_ru = models.TextField(blank=True, default='')
    timing_en = models.TextField(blank=True, default='')
    
    sources_uz = models.TextField(blank=True, default='')
    sources_ru = models.TextField(blank=True, default='')
    sources_en = models.TextField(blank=True, default='')
    
    img = models.ImageField(upload_to='supplements/', blank=True, null=True)

    def __str__(self):
        return self.name_en

class Conversation(models.Model):
    user1 = models.ForeignKey(User, related_name='conversations_started', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='conversations_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        u1_name = self.user1.full_name or self.user1.email
        u2_name = self.user2.full_name or self.user2.email
        return f"{u1_name} & {u2_name}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

# ───── Tracking: Workouts ─────
class WorkoutLog(models.Model):
    """A single training day's diary entry (e.g. 'Monday - Day 1')."""
    user = models.ForeignKey(User, related_name='workout_logs', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate, db_index=True)
    notes = models.TextField(blank=True, default='')
    # Which day of the user's active program (if any) this session followed —
    # lets weekly stats report "N of M program days completed" without
    # forcing every log to be tied to a program.
    program_day = models.ForeignKey('UserProgramDay', related_name='logs', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.date}"

class WorkoutExerciseEntry(models.Model):
    """One exercise performed within a WorkoutLog (e.g. 'Barbell Curl')."""
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('legs', 'Legs'),
        ('abs', 'Abs'),
        ('glutes', 'Glutes'),
    ]

    workout_log = models.ForeignKey(WorkoutLog, related_name='exercises', on_delete=models.CASCADE)
    # Optional link to the exercise catalog — kept nullable so a deleted/renamed
    # catalog entry never breaks a user's historical log. `name` is always the
    # source of truth for display, resolved at creation time from either the
    # catalog or freeform user input.
    exercise = models.ForeignKey(Exercise, related_name='+', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    # Always chosen by the user at log time (never inferred from the catalog),
    # since the catalog's free-text `muscles_*` fields don't map cleanly to a
    # fixed set of weekly-volume categories.
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

class WorkoutSet(models.Model):
    """A single set (weight x reps) within a WorkoutExerciseEntry."""
    exercise_entry = models.ForeignKey(WorkoutExerciseEntry, related_name='sets', on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField(default=1)
    weight_kg = models.FloatField(default=0)
    reps = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['set_number']

    def __str__(self):
        return f"Set {self.set_number}: {self.weight_kg}kg x {self.reps}"

# ───── Tracking: User Programs (personal workout splits) ─────
class UserProgram(models.Model):
    """A user's own editable workout split (e.g. 'Push/Pull/Legs'), either
    built from scratch or copied from the catalog Program — copying takes a
    snapshot, so editing it afterwards never touches the catalog or other
    users. Exactly one program per user may be `is_active` at a time
    (enforced in the view, not here, to keep this a plain model)."""
    user = models.ForeignKey(User, related_name='workout_programs', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.name}"

class UserProgramDay(models.Model):
    """A reusable day slot within a UserProgram (e.g. '1-kun (Ko'krak)').
    Not tied to a calendar weekday — the user picks which day they're doing
    each time they log a workout."""
    program = models.ForeignKey(UserProgram, related_name='days', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.program.name} — {self.name}"

class UserProgramExercise(models.Model):
    """One exercise template within a UserProgramDay. No sets/reps/weight
    targets are stored here — those are entered for real each time the day
    is actually logged; this is just "what to do," not "how much"."""
    day = models.ForeignKey(UserProgramDay, related_name='exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, related_name='+', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    muscle_group = models.CharField(max_length=20, choices=WorkoutExerciseEntry.MUSCLE_GROUP_CHOICES, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

# ───── Tracking: Nutrition ─────
class NutritionLog(models.Model):
    """A single food/meal entry logged by the user for a given day."""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Nonushta'),
        ('lunch', 'Tushlik'),
        ('dinner', 'Kechki ovqat'),
        ('pre_workout', 'Mashqdan oldin'),
        ('post_workout', 'Mashqdan keyin'),
        ('other', 'Boshqa'),
    ]
    user = models.ForeignKey(User, related_name='nutrition_logs', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate, db_index=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='other')
    name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField(default=0)
    protein_g = models.FloatField(default=0)
    carbs_g = models.FloatField(default=0)
    fat_g = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.date} — {self.name}"
