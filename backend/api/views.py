from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import User, Subscription, Plan, UserPlan, Category
from .serializers import (
    SubscriptionSerializer,
    PlanSerializer,
    UserPlanSerializer,
    CategorySerializer,
)
from . import screentime, notifications
import datetime


class UpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        users = User.objects.exclude(api_key_encrypted__isnull=True)

        for user in users:
            if (user.username!='tonyl'): continue
            api_key = user.api_key_encrypted

            # Fetch active plans for the user
            plans = UserPlan.objects.filter(user=user, track_usage=True).select_related("plan__subscription")
            subscription_names = [plan.plan.subscription.name for plan in plans]

            # Fetch screen time data
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            end_date = datetime.date.today().isoformat()
            data = screentime.fetch_data(api_key, start_date, end_date)

            # Calculate usage scores
            usage_scores, df = screentime.calculate_usage(subscription_names, data)
            screentime.display_subscriptions(subscription_names, df)

            # Update usage scores and send notifications for unused subscriptions
            for plan in plans:
                subscription_name = plan.plan.subscription.name
                plan.usage_score = usage_scores.get(subscription_name, 0)
                plan.save()

                if plan.usage_score < 3:
                    notifications.send_push_notification(
                        "Unused Subscription",
                        f"The subscription '{subscription_name}' is unused.",
                        user.id
                    )

        return Response(usage_scores, status=status.HTTP_200_OK)


class GetUserId(APIView):
    def get(self, request):
        return Response({"user_id": request.user.id}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Both username and password must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "A user with that username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(username=username, password=password)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class PlanView(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Apply filters based on query parameters
        filters = Q()
        if cost_min := params.get("cost_min"):
            filters &= Q(cost__gte=cost_min)
        if cost_max := params.get("cost_max"):
            filters &= Q(cost__lte=cost_max)
        if period := params.get("period"):
            filters &= Q(period=period)
        if name := params.get("name"):
            filters &= Q(name__icontains=name)
        if category_id := params.get("category_id"):
            filters &= Q(subscription__category__id=category_id)
        if subscription_name := params.get("subscription_name"):
            filters &= Q(subscription__name__icontains=subscription_name)

        return queryset.filter(filters)


class UserPlanView(viewsets.ModelViewSet):
    serializer_class = UserPlanSerializer

    def get_queryset(self):
        return UserPlan.objects.filter(user=self.request.user)

    def create(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")

        plan = get_object_or_404(Plan, id=plan_id)

        if UserPlan.objects.filter(user=user, plan=plan).exists():
            return Response(
                {"error": "Plan already added to your subscriptions."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_plan = UserPlan.objects.create(
            user=user,
            plan=plan,
        )

        return Response(
            self.get_serializer(user_plan).data,
            status=status.HTTP_201_CREATED,
        )


class SubscriptionView(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer