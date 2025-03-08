from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404
from django.db.models import (
    Q,
    F,
    Sum,
    ExpressionWrapper,
    FloatField,
    DecimalField,
)
from django.db.models.functions import Cast, Coalesce
from decimal import Decimal, InvalidOperation

from .models import *
from .serializers import *

from datetime import date, timedelta
from . import screentime, notifications
from .utils import budget_plans

import datetime


class AverageSpendingPerPeriod(APIView):
    def get(self, request):
        user = request.user
        period_param = request.query_params.get("period", None)

        try:
            # Get all user plans with related data
            user_plans = user.user_plans.select_related("plan").only(
                "plan__cost", "plan__period"
            )

            # Get valid period options
            period_choices = Plan.Period.choices
            target_periods = []

            if period_param:
                # Validate requested period
                target_days = Plan.Period.get_days(period_param)
                period_label = Plan.Period.get_label(target_days)
                target_periods = [(target_days, period_label)]
            else:
                # Use all periods if none specified
                target_periods = period_choices

            results = {}

            for period_days, period_label in target_periods:
                # Calculate normalized costs in database
                avg_expr = Coalesce(
                    (
                        Sum("plan__cost")
                        / (Cast("plan__period", DecimalField()) / period_days)
                    ),
                    Decimal(0),
                )

                aggregate = user_plans.aggregate(average=avg_expr)

                results[period_label] = round(float(aggregate["average"]), 2)

            return Response(results, status=status.HTTP_200_OK)

        except ValueError as e:
            valid_periods = [label for _, label in Plan.Period.choices]
            return Response(
                {"error": f"Invalid period. Valid options: {valid_periods}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TotalSpendingPerPeriod(APIView):
    def get(self, request):
        user = request.user
        today = date.today()

        days = request.query_params.get("days", None)

        spending_per_period = {}

        if days:
            start_date = today - timedelta(days=int(days))
            user_plans = UserPlan.objects.filter(
                user=user, payment_date__range=[start_date, today]
            )
            total_spending = user_plans.aggregate(total=Sum("plan__cost"))["total"] or 0
            spending_per_period[f"past_{days}_days"] = float(total_spending)
        else:
            # Calculate user's spending per period
            user_plans = UserPlan.objects.filter(user=user)

            spending_per_period = {
                "past_day": 0,
                "past_week": 0,
                "past_month": 0,
                "past_quarter": 0,
                "past_year": 0,
            }

            for user_plan in user_plans:
                period = user_plan.plan.period

                start_date = today - timedelta(days=period)

                period_plans = user_plans.filter(payment_date__range=[start_date, today])

                total_spending = (
                    period_plans.aggregate(total=Sum("plan__cost"))["total"] or 0
                )

                period_name = f"past_{user_plan.plan.get_period_display()}"
                spending_per_period[period_name] = float(total_spending)

        return Response(spending_per_period, status=status.HTTP_200_OK)


class SpendingByCategory(APIView):
    def get(self, request):
        user = request.user
        user_plans = UserPlan.objects.filter(user=user).select_related(
            'plan__subscription__category'
        )

        # Get all period labels from Plan model
        period_labels = [label for _, label in Plan.Period.choices]
        totals = {period: 0.0 for period in period_labels}
        spending_data = {}

        for user_plan in user_plans:
            plan = user_plan.plan
            category = plan.subscription.category
            cost = float(plan.cost)
            period_days = plan.period

            if period_days == 0: # Avoid divide by zero error
                continue

            daily_cost = cost / period_days

            # Calculate costs for all periods
            for target_period in period_labels:
                target_days = Plan.Period.get_days(target_period)
                period_cost = daily_cost * target_days

                if category.name not in spending_data:
                    spending_data[category.name] = {
                        'icon': category.icon_emoji,
                        'costs': {p: 0.0 for p in period_labels},
                        'percentages': {p: 0.0 for p in period_labels},
                    }

                spending_data[category.name]['costs'][target_period] += period_cost
                totals[target_period] += period_cost

        # Calculate percentages and format response
        for category, data in spending_data.items():
            for period in period_labels:
                total = totals[period]
                period_cost = data['costs'][period]
                
                data['percentages'][period] = round(
                    (period_cost / total * 100) if total != 0 else 0,
                    2
                )

            # Format costs to 2 decimal places
            data['costs'] = {k: round(v, 2) for k, v in data['costs'].items()}

        return Response(spending_data, status=status.HTTP_200_OK)


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
            user_plans = UserPlan.objects.filter(user=user)

            for user_plan in user_plans:
                user_plan.update_payment_date()

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


class UserSettingsView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSettingsSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSettingsSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
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
        today = date.today()

        # Extract and validate all params at the beginning
        params = self._parse_and_validate_params(self.request.query_params)

        # Build filters
        filters = self._build_filters(params, today)

        # Apply cost annotations if needed
        if params.get("period"):
            queryset = self._annotate_cost(queryset, params["period"])

        # Apply cost filters
        queryset = self._apply_cost_filters(queryset, params)

        return queryset.filter(filters).select_related(
            "plan", "plan__subscription", "plan__subscription__category"
        )

    def _parse_and_validate_params(self, query_params):
        params = {}

        # Category filter
        params["category_id"] = query_params.get("category_id")

        # Track usage filter
        if track_usage := query_params.get("track_usage"):
            if track_usage.lower() not in ["true", "false"]:
                raise ValidationError("track_usage must be 'true' or 'false'")
            params["track_usage"] = track_usage.lower() == "true"

        # Period handling
        if period_str := query_params.get("period"):
            try:
                params["period"] = Plan.Period.get_days(period_str)
            except ValueError as e:
                raise ValidationError(str(e))

        # Cost range
        try:
            params["cost_min"] = (
                Decimal(query_params.get("cost_min"))
                if query_params.get("cost_min")
                else None
            )
            params["cost_max"] = (
                Decimal(query_params.get("cost_max"))
                if query_params.get("cost_max")
                else None
            )
        except InvalidOperation:
            raise ValidationError("Invalid cost value - must be a number")

        # Date filters
        for param_name in ["days_until_payment", "recently_paid"]:
            if days_str := query_params.get(param_name):
                try:
                    days = int(days_str)
                    if days < 0:
                        raise ValueError
                    params[param_name] = days
                except ValueError:
                    raise ValidationError(f"{param_name} must be a positive integer")

        return params

    def _build_filters(self, params, today):
        """Build query filters based on parameters"""
        filters = Q()

        if category_id := params.get("category_id"):
            filters &= Q(plan__subscription__category__id=category_id)

        if track_usage := params.get("track_usage", None):
            filters &= Q(track_usage=track_usage)

        # Payment date filters
        if days := params.get("days_until_payment"):
            end_date = today + timedelta(days=days)
            filters &= Q(payment_date__range=[today, end_date])

        if days := params.get("recently_paid"):
            start_date = today - timedelta(days=days)
            filters &= Q(payment_date__range=[start_date, today])

        return filters

    def _annotate_cost(self, queryset, target_period):
        """Annotate queryset with normalized cost for the target period"""
        return queryset.annotate(
            cost=ExpressionWrapper(
                (F("plan__cost") * target_period)
                / Cast(F("plan__period"), DecimalField()),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )

    def _apply_cost_filters(self, queryset, params):
        """Apply cost range filters to the queryset"""
        if cost_min := params.get("cost_min"):
            queryset = queryset.filter(cost__gte=cost_min)
        if cost_max := params.get("cost_max"):
            queryset = queryset.filter(cost__lte=cost_max)
        return queryset

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
            payment_date = datetime.datetime.strptime(payment_date_str, "%Y-%m-%d").date()
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


class SetBudgetView(APIView):
    def get(self, request):
        try:
            budget = self._get_budget_param(request.query_params)
            period = self._get_period_param(request.query_params.get("period", "month"))

            filters = self._build_filters(
                request.user, request.query_params.get("category_id")
            )

            budget_candidate_plans = self._get_annotated_plans(filters, period)

            candidate_data = list(
                budget_candidate_plans.values("id", "cost", "usage_score")
            )
            print(candidate_data, request.query_params.get("category_id"), budget)

            budget_plan_ids = budget_plans(candidate_data, budget)

            excluded_plans = budget_candidate_plans.exclude(id__in=budget_plan_ids)

            return Response(
                {"subscriptions": UserPlanSerializer(excluded_plans, many=True).data},
                status=status.HTTP_200_OK,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_budget_param(self, query_params):
        try:
            budget = float(query_params.get("budget"))
            if budget < 0:
                raise ValidationError("Budget must be a positive number")
            return budget
        except (ValueError, TypeError):
            raise ValidationError("Invalid budget value")

    def _get_period_param(self, period_str):
        try:
            return Plan.Period.get_days(period_str)
        except ValueError as e:
            raise ValidationError(str(e))

    def _build_filters(self, user, category_id):
        filters = Q(user=user)
        if category_id:
            filters &= Q(plan__subscription__category_id=category_id)
        return filters

    def _get_annotated_plans(self, filters, period):
        return UserPlan.objects.filter(filters).annotate(
            cost=ExpressionWrapper(
                F("plan__cost") / F("plan__period") * period, output_field=FloatField()
            )
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


class ToggleUsageView(APIView):
    def patch(self, request, pk):
        try:
            user_plan = UserPlan.objects.get(pk=pk, user=request.user)
        except UserPlan.DoesNotExist:
            return Response(
                {"error": "UserPlan not found."}, status=status.HTTP_404_NOT_FOUND
            )

        track_usage = request.data.get("track_usage")

        if track_usage is None:
            return Response(
                {"error": "'track_usage' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(track_usage, bool):
            return Response(
                {"error": "'track_usage' must be a boolean value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_plan.track_usage = track_usage
        user_plan.save()

        return Response({"track_usage": user_plan.track_usage}, status=status.HTTP_200_OK)


class PlanView(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
