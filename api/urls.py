from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    ExerciseViewSet, ProgramViewSet, CategoryViewSet,
    MotivationViewSet, DietViewSet, SupplementViewSet
)
from api.auth_views import (
    RegisterView, VerifyEmailView, LoginView, MeView, ResendOTPView,
    PasswordResetRequestView, PasswordResetConfirmView, AddXPView
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'motivation', MotivationViewSet)
router.register(r'diet', DietViewSet)
router.register(r'supplements', SupplementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/add-xp/', AddXPView.as_view(), name='add-xp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
