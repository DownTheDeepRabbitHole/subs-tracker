from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

router = DefaultRouter()
router.register('plans', PlanView, basename='plans')
router.register('user-plans', UserPlanView, basename='user-plans')
router.register('subscriptions', SubscriptionView, basename='subscriptions')
router.register('categories', CategoryView, basename='categories')

auth_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('register/', RegisterView.as_view(), name='register'),
]

user_urlpatterns = [
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('update/', UpdateView.as_view(), name='update-profile'),
    path('update-unused/', UpdateUnusedView.as_view(), name='update-unused'),
    path('get-user-id/', GetUserId.as_view(), name='get-user-id'),
]

analytics_urlpatterns = [
    path('total-spending-per-period/', TotalSpendingPerPeriod.as_view(), name='total-spending-per-period'),
    path('spending-by-category/', SpendingByCategory.as_view(), name='spending-by-category'),
    path('usage-by-category/', UsageByCategory.as_view(), name='usage-by-category'),
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),  # Authentication
    path('user/', include(user_urlpatterns)),  # User-related
    path('analytics/', include(analytics_urlpatterns)),  # Analytics
    path('', include(router.urls)),  # ModelViewSet
]