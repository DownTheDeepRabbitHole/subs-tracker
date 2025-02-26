from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Sum

from .models import User, Subscription, Plan, UserPlan, Category
from .serializers import (
    SubscriptionSerializer,
    PlanSerializer,
    UserPlanSerializer,
    CategorySerializer,
    UserSettingsSerializer,
)

from datetime import date, timedelta
from . import screentime, notifications
from .utils import budget_plans

import datetime

class TotalSpendingPerPeriod(APIView):
    def get(self, request):
        user = request.user
        # Get the current date
        today = date.today()

        # Get query parameters for custom time ranges
        days = request.query_params.get("days", None)

        # Define default time ranges
        time_ranges = {
            "past_week": today - timedelta(days=7),
            "past_month": today - timedelta(days=30),
            "past_year": today - timedelta(days=365),
        }

        # Add custom time range if provided
        if days:
            time_ranges[f"past_{days}_days"] = today - timedelta(days=int(days))

        # Initialize response dictionary
        spending_per_period = {}

        # Calculate spending for each time range
        for period_name, start_date in time_ranges.items():
            # Filter UserPlans within the time range
            user_plans = UserPlan.objects.filter(
                user=user, payment_date__range=[start_date, today]
            )

            # Aggregate total spending for the time range
            total_spending = user_plans.aggregate(total=Sum("plan__cost"))["total"] or 0

            # Add to the response
            spending_per_period[period_name] = float(total_spending)

        return Response(spending_per_period, status=status.HTTP_200_OK)


class SpendingByCategory(APIView):

    @staticmethod
    def calculate_time_range_multipliers(time_ranges):
        time_range_multipliers = {}

        # Generate multipliers based on time ranges
        for name, days in time_ranges.items():
            multipliers = [
                days / period_days for period_name, period_days in time_ranges.items()
            ]
            time_range_multipliers[name] = multipliers

        return time_range_multipliers

    def get(self, request):
        user = request.user
        user_plans = UserPlan.objects.filter(user=user)

        # Define the time ranges (in days): weekly, monthly, yearly
        time_ranges = {
            "day": 1,
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365,
        }

        # Get the time range multipliers for converting payment periods to weekly, monthly, yearly
        time_range_multipliers = self.calculate_time_range_multipliers(time_ranges)

        # Initialize a dictionary to store spending by category
        spending_by_category = {}

        for user_plan in user_plans:
            category = user_plan.plan.subscription.category.name
            cost = user_plan.plan.cost
            period = user_plan.plan.period

            # Ensure the period is valid and exists in the multipliers
            if period not in time_range_multipliers:
                raise ValueError(f"Invalid payment period: {period}")

            # Get the multipliers for the current period
            multipliers = time_range_multipliers[period]

            # Ensure we have the correct multipliers for weekly, monthly, and yearly
            # We need to map multipliers to week, month, and year by checking the corresponding time range
            payments_per_week = None
            payments_per_month = None
            payments_per_year = None

            for multiplier, (range_name, period_days) in zip(
                multipliers, time_ranges.items()
            ):
                if range_name == "week":
                    payments_per_week = multiplier
                elif range_name == "month":
                    payments_per_month = multiplier
                elif range_name == "year":
                    payments_per_year = multiplier

            # Check that all multipliers were found
            if (
                payments_per_week is None
                or payments_per_month is None
                or payments_per_year is None
            ):
                raise ValueError(
                    f"Could not find multipliers for all time ranges in {period}"
                )

            # Initialize the category dictionary if it doesn't exist
            if category not in spending_by_category:
                spending_by_category[category] = {"weekly": 0, "monthly": 0, "yearly": 0}

            # Calculate total spending for each time range (weekly, monthly, yearly)
            spending_by_category[category]["weekly"] += round(float(cost) * payments_per_week, 2)
            spending_by_category[category]["monthly"] += round(float(cost) * payments_per_month, 2)
            spending_by_category[category]["yearly"] += round(float(cost) * payments_per_year, 2)

        return Response(spending_by_category, status=status.HTTP_200_OK)


class UsageByCategory(APIView):
    def get(self, request):
        user = request.user

        user_plans = UserPlan.objects.filter(user=user)
        usage_by_category = {}

        for user_plan in user_plans:
            category = user_plan.plan.subscription.category.name
            usage_score = user_plan.usage_score

            if category not in usage_by_category:
                usage_by_category[category] = 0
            usage_by_category[category] += usage_score

        return Response(usage_by_category, status=status.HTTP_200_OK)


class UpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        users = User.objects.filter(allow_notifications=True)

        today = datetime.datetime.today().date()

        for user in users:
            # Get all user plans for the current user
            user_plans = UserPlan.objects.filter(user=user)

            for user_plan in user_plans:
                # Update the payment_date based on the plan's period
                user_plan.update_payment_date()

                # Check if the next payment is within 3 days
                if user_plan.payment_date - today <= datetime.timedelta(days=3):
                    notifications.send_push_notification(
                        "Upcoming payment",
                        f"{user_plan.plan.subscription.name} is due at {user_plan.payment_date}",
                        user.id,
                    )

        return Response(
            {"message": "Subscription payments updated and notifications sent."},
            status=status.HTTP_200_OK,
        )


class UpdateUnusedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        users = User.objects.exclude(api_key_encrypted__isnull=True)

        for user in users:
            api_key = user.api_key_encrypted

            # Fetch active plans for the user
            user_plans = UserPlan.objects.filter(
                user=user, track_usage=True
            ).select_related("plan__subscription")

            # Fetch screen time data
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            end_date = datetime.date.today().isoformat()
            df = screentime.fetch_data(api_key, start_date, end_date)

            # Update usage scores
            for user_plan in user_plans:
                try:
                    subscription_name = user_plan.plan.subscription.name
                    user_plan.update_usage_score(subscription_name, df)
                except Exception as e:
                    print(f"Error processing {subscription_name}: {e}")

            # Send notifications for unused subscriptions
            if user.allow_notifications:
                unused_threshold = user.unused_threshold

                for user_plan in user_plans:
                    subscription_name = user_plan.plan.subscription.name

                    if user_plan.usage_score < unused_threshold:
                        notifications.send_push_notification(
                            "Unused Subscription",
                            f"The subscription '{subscription_name}' is unused.",
                            user.id,
                        )
                    # (Admin purposes) Display subscriptions after processing all user plans
                    screentime.display_subscriptions(subscription_name, df)

        return Response(
            {"message": "Subscription usage updated and notifications sent."},
            status=status.HTTP_200_OK,
        )


class OptimizeBudget(APIView):
    def get(self, request):
        user = request.user
        budget = request.budget

        user_plans = list(
            UserPlan.objects.filter(user=user).values(
                "id", "usage_score", plan_cost=F("plan__cost")
            )
        )

        selected_ids = budget_plans(user_plans, budget)

        optimized_subs = Subscription.objects.filter(id__in=selected_ids)

        return Response({"subscriptions": optimized_subs}, status=status.HTTP_200_OK)

class UserSettingsView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSettingsSerializer(user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user 
        serializer = UserSettingsSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save updated settings
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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


class UserPlanView(viewsets.ModelViewSet):
    serializer_class = UserPlanSerializer

    def get_queryset(self):
        queryset = UserPlan.objects.filter(user=self.request.user)
        params = self.request.query_params

        # Apply filters based on query parameters
        filters = Q()
        if cost_min := params.get("cost_min"):
            filters &= Q(plan__cost__gte=cost_min)
        if cost_max := params.get("cost_max"):
            filters &= Q(plan__cost__lte=cost_max)
        if period := params.get("period"):
            filters &= Q(plan__period=period)
        if category_id := params.get("category_id"):
            filters &= Q(plan__subscription__category__id=category_id)
        if usage_score := params.get("usage_score"):
            filters &= Q(usage_score=usage_score)
        if track_usage := params.get("track_usage"):
            filters &= Q(track_usage=track_usage.lower() == "true")

        return queryset.filter(filters)

    def create(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")
        payment_date_str = request.data.get("payment_date")

        plan = get_object_or_404(Plan, id=plan_id)

        # Check if the user already has this plan
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            return Response(
                {"error": "Plan already added to your subscriptions."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_plan = UserPlan.objects.create(
            user=user, plan=plan, payment_date=payment_date
        )

        serialized_data = self.get_serializer(user_plan).data

        return Response(
            serialized_data,
            status=status.HTTP_201_CREATED,
        )


class SubscriptionView(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Apply filters based on query parameters
        filters = Q()
        if cost_min := params.get("cost_min"):
            filters &= Q(plan__cost__gte=cost_min)
        if cost_max := params.get("cost_max"):
            filters &= Q(plan__cost__lte=cost_max)
        if period := params.get("period"):
            filters &= Q(plan__period=period)
        if category_id := params.get("category_id"):
            filters &= Q(category__id=category_id)

        return queryset.filter(filters)

class PlanView(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
