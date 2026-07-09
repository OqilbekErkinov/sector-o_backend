from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    ExerciseViewSet, ProgramViewSet, CategoryViewSet,
    MotivationViewSet, DietViewSet, SupplementViewSet
)
from api.auth_views import (
    RegisterView, VerifyEmailView, LoginView, MeView, ResendOTPView,
    PasswordResetRequestView, PasswordResetConfirmView, AddXPView, RankingsView,
    ConfirmEmailChangeView
)
from api.chat_views import (
    ConversationListView, StartConversationView, MessageListView, WSTicketView
)
from api.tracking_views import (
    WorkoutLogListCreateView, WorkoutLogDetailView, WorkoutSummaryView,
    WorkoutComparisonView, WorkoutExportView,
    NutritionLogListCreateView, NutritionLogDetailView, NutritionSummaryView,
    NutritionExportView,
)
from api.user_program_views import (
    UserProgramListCreateView, UserProgramDetailView, UserProgramActivateView,
    ActiveUserProgramView, CopyProgramFromCatalogView,
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
    path('auth/confirm-email-change/', ConfirmEmailChangeView.as_view(), name='confirm-email-change'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/add-xp/', AddXPView.as_view(), name='add-xp'),
    path('auth/rankings/', RankingsView.as_view(), name='rankings'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Chat URLs
    path('chat/conversations/', ConversationListView.as_view(), name='chat-conversations'),
    path('chat/conversations/start/', StartConversationView.as_view(), name='chat-start'),
    path('chat/conversations/<int:pk>/messages/', MessageListView.as_view(), name='chat-messages'),
    path('chat/ws-ticket/', WSTicketView.as_view(), name='chat-ws-ticket'),

    # Tracking (workout & nutrition diary)
    path('tracking/workouts/summary/', WorkoutSummaryView.as_view(), name='workout-summary'),
    path('tracking/workouts/comparison/', WorkoutComparisonView.as_view(), name='workout-comparison'),
    path('tracking/workouts/export/', WorkoutExportView.as_view(), name='workout-export'),
    path('tracking/workouts/', WorkoutLogListCreateView.as_view(), name='workout-logs'),
    path('tracking/workouts/<int:pk>/', WorkoutLogDetailView.as_view(), name='workout-log-detail'),
    path('tracking/nutrition/summary/', NutritionSummaryView.as_view(), name='nutrition-summary'),
    path('tracking/nutrition/export/', NutritionExportView.as_view(), name='nutrition-export'),
    path('tracking/nutrition/', NutritionLogListCreateView.as_view(), name='nutrition-logs'),
    path('tracking/nutrition/<int:pk>/', NutritionLogDetailView.as_view(), name='nutrition-log-detail'),

    # User workout programs (personal splits)
    path('user-programs/active/', ActiveUserProgramView.as_view(), name='user-program-active'),
    path('user-programs/copy-from-catalog/', CopyProgramFromCatalogView.as_view(), name='user-program-copy'),
    path('user-programs/<int:pk>/activate/', UserProgramActivateView.as_view(), name='user-program-activate'),
    path('user-programs/', UserProgramListCreateView.as_view(), name='user-programs'),
    path('user-programs/<int:pk>/', UserProgramDetailView.as_view(), name='user-program-detail'),
]
