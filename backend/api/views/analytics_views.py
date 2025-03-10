from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.db.models import (
    Q,
    F,
    Sum,
    ExpressionWrapper,
    FloatField,
    DecimalField,
)
from django.db.models.functions import Cast, Coalesce
from decimal import Decimal

from ..models import Plan, UserPlan
from ..serializers import UserPlanSerializer
from ..services import SpendingCalculator, AverageSpendingCalculator
from ..serializers import PeriodQueryParamSerializer

from ..utils import budget_plans


class AverageSpendingPerPeriod(APIView):
    """Gets normalized total spending for each period"""

    def get(self, request):
        user = request.user

        try:
            # Validate and parse parameters
            serializer = PeriodQueryParamSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            period_param = serializer.validated_data.get("period", None)

            # Determine target periods
            if period_param:
                target_periods = [(period_param, Plan.Period.get_label(period_param))]
            else:
                target_periods = Plan.Period.choices

            # Calculate results
            calculator = AverageSpendingCalculator(UserPlan.objects.filter(user=user))
            results = calculator.calculate_averages(target_periods)

            return Response(results)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class TotalSpendingPerPeriod(APIView):
    """Retrieving total spending in the past __ period"""

    def get(self, request):
        user = request.user
        days_param = request.query_params.get("days")

        calculator = SpendingCalculator(UserPlan.objects.filter(user=user))

        try:
            if days_param:
                days = self._validate_days_param(days_param)
                total = calculator.calculate_custom_spending(days)
                return Response({f"past_{days}_days": total})

            totals = calculator.calculate_spending(SpendingCalculator.DEFAULT_PERIODS)
            return Response(totals)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

    def _validate_days_param(self, days_str: str) -> int:
        """Validate and parse days query parameter."""
        try:
            days = int(days_str)
            if days <= 0:
                raise ValueError
            return days
        except ValueError:
            raise ValidationError("Days parameter must be a positive integer")


class SpendingByCategory(APIView):
    def get(self, request):
        user = request.user
        user_plans = UserPlan.objects.filter(user=user).select_related(
            "plan__subscription__category"
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

            if period_days == 0:  # Avoid divide by zero error
                continue

            daily_cost = cost / period_days

            # Calculate costs for all periods
            for target_period in period_labels:
                target_days = Plan.Period.get_days(target_period)
                period_cost = daily_cost * target_days

                if category.name not in spending_data:
                    spending_data[category.name] = {
                        "icon": category.icon_emoji,
                        "costs": {p: 0.0 for p in period_labels},
                        "percentages": {p: 0.0 for p in period_labels},
                    }

                spending_data[category.name]["costs"][target_period] += period_cost
                totals[target_period] += period_cost

        # Calculate percentages and format response
        for category, data in spending_data.items():
            for period in period_labels:
                total = totals[period]
                period_cost = data["costs"][period]

                data["percentages"][period] = round(
                    (period_cost / total * 100) if total != 0 else 0, 2
                )

            # Format costs to 2 decimal places
            data["costs"] = {k: round(v, 2) for k, v in data["costs"].items()}

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

            budget_plan_ids = budget_plans(candidate_data, budget)

            included_plans = budget_candidate_plans.filter(id__in=budget_plan_ids)
            excluded_plans = budget_candidate_plans.exclude(id__in=budget_plan_ids)

            return Response(
                {
                    "included_plans": UserPlanSerializer(included_plans, many=True).data,
                    "excluded_plans": UserPlanSerializer(excluded_plans, many=True).data,
                },
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
