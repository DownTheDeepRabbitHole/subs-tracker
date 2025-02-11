from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, SubscriptionView, PlanView, UserPlanView, CategoryView, UpdateView, GetUserId

# Create the router for the ModelViewSet
router = DefaultRouter()
router.register('plans', PlanView, basename='plans')
router.register('user-plans', UserPlanView, basename='user-plans')
router.register('subscriptions', SubscriptionView, basename='subscriptions')
router.register('categories', CategoryView, basename='category')

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterView.as_view(), name='register'),
    path('update/', UpdateView.as_view(), name='update'),
    path('get-user-id/', GetUserId.as_view(), name='get_user_id'),
    *router.urls,
]