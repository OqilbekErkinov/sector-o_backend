from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import OTPCode
from api.telegram_utils import send_telegram_message

User = get_user_model()


def get_user_lang(request):
    lang = request.data.get('lang')
    if not lang:
        lang_header = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if lang_header:
            primary_lang = lang_header.split(',')[0].split('-')[0].lower()
            if primary_lang in ['uz', 'ru', 'en']:
                lang = primary_lang
            else:
                lang = 'uz'
        else:
            lang = 'uz'
    return lang


def get_api_messages(lang):
    msgs = {
        'uz': {
            'email_pass_req': 'Email va parol majburiy',
            'pass_length': 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak',
            'email_exists': 'Bu email allaqachon ro\'yxatdan o\'tgan',
            'register_success': 'Ro\'yxatdan o\'tish muvaffaqiyatli. Emailingizga tasdiqlash kodi yuborildi.',
            'email_code_req': 'Email va kod majburiy',
            'user_not_found': 'Foydalanuvchi topilmadi',
            'invalid_code': 'Noto\'g\'ri kod',
            'code_expired': 'Kod muddati o\'tgan yoki mavjud emas. Qayta yuborish uchun boshqa so\'rov yuboring.',
            'verify_success': 'Email tasdiqlandi!',
            'wrong_creds': 'Email yoki parol noto\'g\'ri',
            'not_verified': 'Email tasdiqlanmagan. Yangi kod yuborildi.',
            'email_taken': 'Bu email allaqachon band',
            'profile_updated': 'Profil muvaffaqiyatli yangilandi',
            'email_req': 'Email majburiy',
            'new_code_sent': 'Yangi kod yuborildi',
            'reset_code_sent': 'Parolni tiklash kodi emailingizga yuborildi.',
            'reset_req_all': 'Email, kod va yangi parol majburiy',
            'reset_success': 'Parolingiz muvaffaqiyatli yangilandi! Endi tizimga kirishingiz mumkin.',
            'invalid_xp': 'Noto\'g\'ri XP qiymati',
            'xp_gt_zero': 'XP 0 dan katta bo\'lishi kerak',
            'xp_added': '{} XP muvaffaqiyatli qo\'shildi!',
            'same_email': 'Bu sizning joriy emailingiz',
            'email_change_code_sent': 'Yangi emailingizga tasdiqlash kodi yuborildi',
            'email_change_success': 'Email muvaffaqiyatli o\'zgartirildi',
            'invalid_avatar': 'Rasm formati yoki hajmi noto\'g\'ri (JPG/PNG/WEBP, 5MB gacha)',
        },
        'ru': {
            'email_pass_req': 'Email и пароль обязательны',
            'pass_length': 'Пароль должен состоять минимум из 6 символов',
            'email_exists': 'Этот email уже зарегистрирован',
            'register_success': 'Регистрация успешна. Код подтверждения отправлен на ваш email.',
            'email_code_req': 'Email и код обязательны',
            'user_not_found': 'Пользователь не найден',
            'invalid_code': 'Неверный код',
            'code_expired': 'Код недействителен или устарел. Отправьте запрос снова.',
            'verify_success': 'Email подтвержден!',
            'wrong_creds': 'Неверный email или пароль',
            'not_verified': 'Email не подтвержден. Отправлен новый код.',
            'email_taken': 'Этот email уже занят',
            'profile_updated': 'Профиль успешно обновлен',
            'email_req': 'Email обязателен',
            'new_code_sent': 'Новый код отправлен',
            'reset_code_sent': 'Код для сброса пароля отправлен на ваш email.',
            'reset_req_all': 'Email, код и новый пароль обязательны',
            'reset_success': 'Ваш пароль успешно обновлен! Теперь вы можете войти.',
            'invalid_xp': 'Неверное значение XP',
            'xp_gt_zero': 'XP должно быть больше 0',
            'xp_added': '{} XP успешно добавлено!',
            'same_email': 'Это ваш текущий email',
            'email_change_code_sent': 'Код подтверждения отправлен на новый email',
            'email_change_success': 'Email успешно изменен',
            'invalid_avatar': 'Неверный формат или размер изображения (JPG/PNG/WEBP, до 5МБ)',
        },
        'en': {
            'email_pass_req': 'Email and password are required',
            'pass_length': 'Password must be at least 6 characters long',
            'email_exists': 'This email is already registered',
            'register_success': 'Registration successful. A verification code has been sent to your email.',
            'email_code_req': 'Email and code are required',
            'user_not_found': 'User not found',
            'invalid_code': 'Invalid code',
            'code_expired': 'Code expired or invalid. Please request a new one.',
            'verify_success': 'Email verified!',
            'wrong_creds': 'Incorrect email or password',
            'not_verified': 'Email not verified. A new code has been sent.',
            'email_taken': 'This email is already taken',
            'profile_updated': 'Profile updated successfully',
            'email_req': 'Email is required',
            'new_code_sent': 'New code sent',
            'reset_code_sent': 'Password reset code has been sent to your email.',
            'reset_req_all': 'Email, code, and new password are required',
            'reset_success': 'Your password has been updated successfully! You can now log in.',
            'invalid_xp': 'Invalid XP value',
            'xp_gt_zero': 'XP must be greater than 0',
            'xp_added': '{} XP added successfully!',
            'same_email': 'This is already your current email',
            'email_change_code_sent': 'A verification code has been sent to your new email',
            'email_change_success': 'Email changed successfully',
            'invalid_avatar': 'Invalid image format or size (JPG/PNG/WEBP, up to 5MB)',
        }
    }
    return msgs.get(lang, msgs['uz'])


def get_email_texts(lang, action='verify'):
    texts = {
        'uz': {
            'greeting_word': 'Assalomu alaykum',
            'footer_rights_text': 'Barcha huquqlar himoyalangan.',
            'footer_ignore_text': "Agar bu so'rovni siz yubormagan bo'lsangiz, bu xatga e'tibor bermang.",
            'verify': {
                'title_text': 'Email tasdiqlash',
                'description_text': 'Sector-O akkauntingizga kirish uchun tasdiqlash kodingiz:',
                'validity_text': 'Kod 10 daqiqa amal qiladi.',
                'warning_bold_text': 'Kodni hech kimga bermang.',
                'warning_text': "Biz hech qachon sizdan parol so'ramaymiz.",
            },
            'reset': {
                'title_text': 'Parolni tiklash kodi',
                'description_text': "Siz parolni tiklashni so'radingiz. Tasdiqlash kodingiz:",
                'validity_text': 'Kod 10 daqiqa amal qiladi.',
                'warning_bold_text': 'Kodni hech kimga bermang.',
                'warning_text': "Parolingiz xavfsizligi o'z qo'lingizda.",
            },
            'change_email': {
                'title_text': 'Emailni tasdiqlash',
                'description_text': "Ushbu emailni akkauntingizga bog'lash uchun tasdiqlash kodi:",
                'validity_text': 'Kod 10 daqiqa amal qiladi.',
                'warning_bold_text': 'Kodni hech kimga bermang.',
                'warning_text': "Agar bu so'rovni siz yubormagan bo'lsangiz, kodni hech kimga bermang.",
            }
        },
        'ru': {
            'greeting_word': 'Здравствуйте',
            'footer_rights_text': 'Все права защищены.',
            'footer_ignore_text': 'Если вы не отправляли этот запрос, проигнорируйте это письмо.',
            'verify': {
                'title_text': 'Подтверждение email',
                'description_text': 'Ваш код подтверждения для входа в аккаунт Sector-O:',
                'validity_text': 'Код действителен 10 минут.',
                'warning_bold_text': 'Никому не сообщайте код.',
                'warning_text': 'Мы никогда не просим ваш пароль.',
            },
            'reset': {
                'title_text': 'Код сброса пароля',
                'description_text': 'Вы запросили сброс пароля. Ваш код подтверждения:',
                'validity_text': 'Код действителен 10 минут.',
                'warning_bold_text': 'Никому не сообщайте код.',
                'warning_text': 'Безопасность вашего пароля в ваших руках.',
            },
            'change_email': {
                'title_text': 'Подтверждение email',
                'description_text': 'Код подтверждения для привязки этого email к вашему аккаунту:',
                'validity_text': 'Код действителен 10 минут.',
                'warning_bold_text': 'Никому не сообщайте код.',
                'warning_text': 'Если вы не запрашивали это, никому не сообщайте код.',
            }
        },
        'en': {
            'greeting_word': 'Hello',
            'footer_rights_text': 'All rights reserved.',
            'footer_ignore_text': "If you didn't request this, please ignore this email.",
            'verify': {
                'title_text': 'Email Verification',
                'description_text': 'Your verification code to access your Sector-O account:',
                'validity_text': 'The code is valid for 10 minutes.',
                'warning_bold_text': 'Do not share this code with anyone.',
                'warning_text': 'We will never ask for your password.',
            },
            'reset': {
                'title_text': 'Password Reset Code',
                'description_text': 'You requested a password reset. Here is your verification code:',
                'validity_text': 'The code is valid for 10 minutes.',
                'warning_bold_text': 'Do not share this code with anyone.',
                'warning_text': 'Your password security is in your hands.',
            },
            'change_email': {
                'title_text': 'Email Verification',
                'description_text': 'Verification code to link this email to your account:',
                'validity_text': 'The code is valid for 10 minutes.',
                'warning_bold_text': 'Do not share this code with anyone.',
                'warning_text': "If you didn't request this, do not share the code with anyone.",
            }
        }
    }
    
    lang_texts = texts.get(lang, texts['uz'])
    action_texts = lang_texts.get(action, lang_texts['verify'])
    
    return {
        'greeting_word': lang_texts['greeting_word'],
        'footer_rights_text': lang_texts['footer_rights_text'],
        'footer_ignore_text': lang_texts['footer_ignore_text'],
        **action_texts
    }


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')
        full_name = request.data.get('full_name', '')
        phone = request.data.get('phone', '')

        if not email or not password:
            return Response({'error': msgs['email_pass_req']}, status=400)

        if len(password) < 6:
            return Response({'error': msgs['pass_length']}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': msgs['email_exists']}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
        )

        otp = OTPCode.objects.create(email=email, purpose='verify')

        texts = get_email_texts(lang, 'verify')
        html_message = render_to_string('api/universal_email_template.html', {
            'full_name': user.full_name or 'User',
            'verification_code': otp.code,
            **texts
        })

        send_mail(
            subject=f"Sector-O — {texts['title_text']}",
            message=f"{texts['greeting_word']}!\n\n{texts['description_text']} {otp.code}\n\n{texts['validity_text']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message,
        )

        return Response({'message': msgs['register_success']}, status=201)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        code = request.data.get('code', '').strip()

        if not email or not code:
            return Response({'error': msgs['email_code_req']}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': msgs['user_not_found']}, status=404)

        otp = OTPCode.objects.filter(email=email, purpose='verify', is_used=False).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            return Response({'error': msgs['code_expired']}, status=400)

        if otp.code != code:
            return Response({'error': msgs['invalid_code']}, status=400)

        otp.is_used = True
        otp.save()

        user.is_active = True
        user.save()

        # Send Telegram notification (only if configured via env vars)
        text = f"🚀 Yangi foydalanuvchi tizimga qo'shildi!\n\n" \
               f"👤 Ismi: {user.full_name}\n" \
               f"📧 Email: {user.email}\n"
        if user.phone:
            text += f"📱 Telefon: {user.phone}"
        send_telegram_message(text)

        tokens = get_tokens_for_user(user)
        return Response({
            'message': msgs['verify_success'],
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'xp': user.xp,
                'level': user.level,
                'weekly_goal': user.weekly_goal,
            'goal_calories': user.goal_calories,
            'goal_protein_g': user.goal_protein_g,
            'goal_carbs_g': user.goal_carbs_g,
            'goal_fat_g': user.goal_fat_g,
                'goal_calories': user.goal_calories,
                'goal_protein_g': user.goal_protein_g,
                'goal_carbs_g': user.goal_carbs_g,
                'goal_fat_g': user.goal_fat_g,
                'workouts_done': user.workouts_done,
                'active_days': user.active_days,
                'current_week_workouts': user.current_week_workouts,
            },
            **tokens
        })


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': msgs['email_pass_req']}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': msgs['wrong_creds']}, status=401)

        if not user.check_password(password):
            return Response({'error': msgs['wrong_creds']}, status=401)

        if not user.is_active:
            OTPCode.objects.filter(email=email, purpose='verify', is_used=False).update(is_used=True)
            otp = OTPCode.objects.create(email=email, purpose='verify')
            texts = get_email_texts(lang, 'verify')
            html_message = render_to_string('api/universal_email_template.html', {
                'full_name': user.full_name or 'User',
                'verification_code': otp.code,
                **texts
            })
            send_mail(
                subject=f"Sector-O — {texts['title_text']}",
                message=f"{texts['greeting_word']}!\n\n{texts['description_text']} {otp.code}\n\n{texts['validity_text']}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message,
            )
            return Response({'error': msgs['not_verified'], 'needs_verification': True}, status=403)

        from api.models import Conversation, Message
        from django.db.models import Q
        unread_conversations_count = Message.objects.filter(
            conversation__in=Conversation.objects.filter(Q(user1=user) | Q(user2=user)),
            is_read=False
        ).exclude(sender=user).values('conversation_id').distinct().count()

        tokens = get_tokens_for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'xp': user.xp,
                'level': user.level,
                'weekly_goal': user.weekly_goal,
            'goal_calories': user.goal_calories,
            'goal_protein_g': user.goal_protein_g,
            'goal_carbs_g': user.goal_carbs_g,
            'goal_fat_g': user.goal_fat_g,
                'goal_calories': user.goal_calories,
                'goal_protein_g': user.goal_protein_g,
                'goal_carbs_g': user.goal_carbs_g,
                'goal_fat_g': user.goal_fat_g,
                'workouts_done': user.workouts_done,
                'active_days': user.active_days,
                'current_week_workouts': user.current_week_workouts,
                'unread_conversations_count': unread_conversations_count,
            },
            **tokens
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        from api.models import Conversation, Message
        from django.db.models import Q
        
        # O'qilmagan xabarlari bor alohida suhbatlar sonini hisoblash
        unread_conversations_count = Message.objects.filter(
            conversation__in=Conversation.objects.filter(Q(user1=user) | Q(user2=user)),
            is_read=False
        ).exclude(sender=user).values('conversation_id').distinct().count()

        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'xp': user.xp,
            'level': user.level,
            'weekly_goal': user.weekly_goal,
            'goal_calories': user.goal_calories,
            'goal_protein_g': user.goal_protein_g,
            'goal_carbs_g': user.goal_carbs_g,
            'goal_fat_g': user.goal_fat_g,
            'workouts_done': user.workouts_done,
            'active_days': user.active_days,
            'current_week_workouts': user.current_week_workouts,
            'img': request.build_absolute_uri(user.img.url) if user.img else None,
            'unread_conversations_count': unread_conversations_count,
        })

    def patch(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)

        user = request.user
        data = request.data

        full_name = data.get('full_name')
        phone = data.get('phone')
        email = data.get('email')
        weekly_goal = data.get('weekly_goal')
        img_data = data.get('img')

        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone
        if weekly_goal is not None:
            try:
                user.weekly_goal = int(weekly_goal)
            except ValueError:
                pass

        goal_calories = data.get('goal_calories')
        if goal_calories is not None:
            try:
                user.goal_calories = max(0, int(goal_calories))
            except (TypeError, ValueError):
                pass
        for field in ('goal_protein_g', 'goal_carbs_g', 'goal_fat_g'):
            value = data.get(field)
            if value is not None:
                try:
                    setattr(user, field, max(0.0, float(value)))
                except (TypeError, ValueError):
                    pass

        email_change_pending = False
        if email is not None:
            email = email.lower().strip()
            if email != user.email:
                if email == '':
                    return Response({'error': msgs['email_req']}, status=400)
                if User.objects.filter(email=email).exists():
                    return Response({'error': msgs['email_taken']}, status=400)
                # Email is NOT changed here — a confirmation code is sent to the
                # new address first; the change only applies once that code is
                # verified via ConfirmEmailChangeView. Prevents account takeover
                # by simply PATCHing someone else's email into your session.
                OTPCode.objects.filter(email=user.email, purpose='change_email', is_used=False).update(is_used=True)
                otp = OTPCode.objects.create(email=user.email, purpose='change_email', new_email=email)
                texts = get_email_texts(lang, 'change_email')
                html_message = render_to_string('api/universal_email_template.html', {
                    'full_name': user.full_name or 'User',
                    'verification_code': otp.code,
                    **texts
                })
                send_mail(
                    subject=f"Sector-O — {texts['title_text']}",
                    message=f"{texts['greeting_word']}!\n\n{texts['description_text']} {otp.code}\n\n{texts['validity_text']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=html_message,
                )
                email_change_pending = True

        if img_data:
            import base64
            from django.core.files.base import ContentFile

            MAX_AVATAR_BYTES = 5 * 1024 * 1024
            ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
            try:
                header, imgstr = img_data.split(';base64,')
                ext = header.split('/')[-1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    return Response({'error': msgs['invalid_avatar']}, status=400)
                decoded = base64.b64decode(imgstr, validate=True)
                if len(decoded) > MAX_AVATAR_BYTES:
                    return Response({'error': msgs['invalid_avatar']}, status=400)
                user.img = ContentFile(decoded, name=f'avatar_{user.id}.{ext}')
            except (ValueError, TypeError):
                return Response({'error': msgs['invalid_avatar']}, status=400)
        elif img_data == "":
            user.img = None

        user.save()
        response_data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'xp': user.xp,
            'level': user.level,
            'weekly_goal': user.weekly_goal,
            'goal_calories': user.goal_calories,
            'goal_protein_g': user.goal_protein_g,
            'goal_carbs_g': user.goal_carbs_g,
            'goal_fat_g': user.goal_fat_g,
            'workouts_done': user.workouts_done,
            'active_days': user.active_days,
            'current_week_workouts': user.current_week_workouts,
            'img': request.build_absolute_uri(user.img.url) if user.img else None,
            'message': msgs['email_change_code_sent'] if email_change_pending else msgs['profile_updated'],
        }
        if email_change_pending:
            response_data['email_change_pending'] = True
        return Response(response_data)


class ConfirmEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'otp'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)

        user = request.user
        code = request.data.get('code', '').strip()
        if not code:
            return Response({'error': msgs['email_code_req']}, status=400)

        otp = OTPCode.objects.filter(
            email=user.email, purpose='change_email', is_used=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            return Response({'error': msgs['code_expired']}, status=400)

        if otp.code != code:
            return Response({'error': msgs['invalid_code']}, status=400)

        if User.objects.filter(email=otp.new_email).exclude(pk=user.pk).exists():
            return Response({'error': msgs['email_taken']}, status=400)

        otp.is_used = True
        otp.save()

        user.email = otp.new_email
        user.save(update_fields=['email'])

        return Response({
            'id': user.id,
            'email': user.email,
            'message': msgs['email_change_success'],
        })


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        if not email:
            return Response({'error': msgs['email_req']}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': msgs['user_not_found']}, status=404)

        OTPCode.objects.filter(email=email, purpose='verify', is_used=False).update(is_used=True)
        otp = OTPCode.objects.create(email=email, purpose='verify')

        texts = get_email_texts(lang, 'verify')
        html_message = render_to_string('api/universal_email_template.html', {
            'full_name': user.full_name or 'User',
            'verification_code': otp.code,
            **texts
        })
        send_mail(
            subject=f"Sector-O — {texts['title_text']}",
            message=f"{texts['greeting_word']}!\n\n{texts['description_text']} {otp.code}\n\n{texts['validity_text']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message,
        )
        return Response({'message': msgs['new_code_sent']})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        if not email:
            return Response({'error': msgs['email_req']}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': msgs['user_not_found']}, status=404)

        OTPCode.objects.filter(email=email, purpose='reset', is_used=False).update(is_used=True)
        otp = OTPCode.objects.create(email=email, purpose='reset')

        texts = get_email_texts(lang, 'reset')
        html_message = render_to_string('api/universal_email_template.html', {
            'full_name': user.full_name or 'User',
            'verification_code': otp.code,
            **texts
        })
        send_mail(
            subject=f"Sector-O — {texts['title_text']}",
            message=f"{texts['greeting_word']}!\n\n{texts['description_text']} {otp.code}\n\n{texts['validity_text']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message,
        )
        return Response({'message': msgs['reset_code_sent']})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp'

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)
        
        email = request.data.get('email', '').lower().strip()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('password', '')

        if not email or not code or not new_password:
            return Response({'error': msgs['reset_req_all']}, status=400)

        if len(new_password) < 6:
            return Response({'error': msgs['pass_length']}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': msgs['user_not_found']}, status=404)

        otp = OTPCode.objects.filter(email=email, purpose='reset', is_used=False).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            return Response({'error': msgs['code_expired']}, status=400)

        if otp.code != code:
            return Response({'error': msgs['invalid_code']}, status=400)

        otp.is_used = True
        otp.save()

        user.set_password(new_password)
        user.save()

        return Response({'message': msgs['reset_success']})


class AddXPView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = 'auth'

    # A training session currently awards 10 XP per exercise (see training.vue).
    # No real session is tracked server-side yet, so this caps the plausible
    # size of a single session to stop arbitrary client-supplied XP values
    # from inflating a user's score/leaderboard rank.
    MAX_XP_PER_REQUEST = 300

    def post(self, request):
        lang = get_user_lang(request)
        msgs = get_api_messages(lang)

        try:
            xp_to_add = int(request.data.get('xp', 0))
        except (TypeError, ValueError):
            return Response({'error': msgs['invalid_xp']}, status=400)

        if xp_to_add <= 0:
            return Response({'error': msgs['xp_gt_zero']}, status=400)

        if xp_to_add > self.MAX_XP_PER_REQUEST:
            return Response({'error': msgs['invalid_xp']}, status=400)

        user = request.user
        
        user.xp += xp_to_add
        user.level = (user.xp // 100) + 1
        
        user.workouts_done += 1
        
        from django.utils import timezone
        today = timezone.now().date()
        
        if user.last_workout_date != today:
            user.active_days += 1
            if user.last_workout_date:
                today_week = today.isocalendar()[:2]
                last_week = user.last_workout_date.isocalendar()[:2]
                if today_week == last_week:
                    user.current_week_workouts += 1
                else:
                    user.current_week_workouts = 1
            else:
                user.current_week_workouts = 1
            user.last_workout_date = today
            
        user.save()
        
        return Response({
            'message': msgs['xp_added'].format(xp_to_add),
            'xp': user.xp,
            'level': user.level,
            'workouts_done': user.workouts_done,
            'active_days': user.active_days,
            'current_week_workouts': user.current_week_workouts
        })

class RankingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.filter(is_active=True).order_by('-xp')[:100]
        data = []
        for index, user in enumerate(users):
            data.append({
                'rank': index + 1,
                'id': user.id,
                'full_name': user.full_name or 'Anonymous',
                'xp': user.xp,
                'level': user.level,
                'img': request.build_absolute_uri(user.img.url) if user.img else None,
            })
        return Response(data)
