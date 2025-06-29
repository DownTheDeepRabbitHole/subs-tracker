from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("plans", PlanView, basename="plans")
router.register("user-plans", UserPlanView, basename="user-plans")
router.register("subscriptions", SubscriptionView, basename="subscriptions")
router.register("categories", CategoryView, basename="categories")

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="login"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("verify/", CookieTokenVerifyView.as_view(), name="token-verify"),
]

user_urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("settings/", UserSettingsView.as_view(), name="settings"),
]

analytics_urlpatterns = [
    path(
        "total-spending-per-period/",
        TotalSpendingPerPeriod.as_view(),
        name="total-spending-per-period",
    ),
    path(
        "average-spending-per-period/",
        AverageSpendingPerPeriod.as_view(),
        name="average-spending-per-period",
    ),
    path(
        "spending-by-category/", SpendingByCategory.as_view(), name="spending-by-category"
    ),
    path("usage-by-category/", UsageByCategory.as_view(), name="usage-by-category"),
    path("set-budget/", SetBudgetView.as_view(), name="set-budget"),
]

cron_urlpatterns = [
    path("payment/", UpdateView.as_view(), name="update-payment-plans"),
    path("unused/", UpdateUnusedView.as_view(), name="update-unused-plans"),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),  # Authentication
    path("user/", include(user_urlpatterns)),  # User-related
    path("analytics/", include(analytics_urlpatterns)),  # Analytics
    path("cron/", include(cron_urlpatterns)),  # Cron jobs
    path(
        "user-plans/<int:pk>/toggle-usage/",
        ToggleUsageView.as_view(),
        name="toggle-usage",
    ),
    path("", include(router.urls)),  # ModelViewSet
]
