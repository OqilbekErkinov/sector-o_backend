from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.text import slugify
import random, string

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

# ───── OTP Code ─────
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

class OTPCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # 10 daqiqa ichida amal qiladi
        from datetime import timedelta
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} — {self.code}"

class Category(models.Model):
    name_uz = models.CharField(max_length=100, default='')
    name_ru = models.CharField(max_length=100, default='')
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
    
    name_uz = models.CharField(max_length=255, default='')
    name_ru = models.CharField(max_length=255, default='')
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

    name_uz = models.CharField(max_length=255, default='')
    name_ru = models.CharField(max_length=255, default='')
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
    name_uz = models.CharField(max_length=255, default='')
    name_ru = models.CharField(max_length=255, default='')
    name_en = models.CharField(max_length=255, default='')
    
    exercises = models.ManyToManyField(Exercise, related_name='program_days')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.program.name_en} - {self.name_en}"

class Motivation(models.Model):
    quote_uz = models.TextField(default='')
    quote_ru = models.TextField(default='')
    quote_en = models.TextField(default='')
    author = models.CharField(max_length=100, blank=True, null=True)

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
    
    title_uz = models.CharField(max_length=255, default='')
    title_ru = models.CharField(max_length=255, default='')
    title_en = models.CharField(max_length=255, default='')
    
    description_uz = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, default='')
    description_en = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.meal_type}: {self.title_en}"

class Supplement(models.Model):
    name_uz = models.CharField(max_length=255, default='')
    name_ru = models.CharField(max_length=255, default='')
    name_en = models.CharField(max_length=255, default='')
    
    benefits_uz = models.TextField(blank=True, default='')
    benefits_ru = models.TextField(blank=True, default='')
    benefits_en = models.TextField(blank=True, default='')
    
    img = models.ImageField(upload_to='supplements/', blank=True, null=True)

    def __str__(self):
        return self.name_en
