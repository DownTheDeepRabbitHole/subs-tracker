from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from django.db.models import (
    Q,
    F,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation

from ..models import *
from ..serializers import *

from datetime import date, timedelta
import datetime

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class UserPlanView(viewsets.ModelViewSet):
    serializer_class = UserPlanSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["payment_date", "plan__name", "track_usage", "usage_score"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        queryset = UserPlan.objects.filter(user=self.request.user)
        today = date.today()

        params = self._parse_and_validate_params(self.request.query_params)
        filters = self._build_filters(params, today)

        # Apply base filters first
        queryset = queryset.filter(filters)

        # Annotate cost if period is specified
        if params.get("period"):
            queryset = self._annotate_cost(queryset, params["period"])

        # Apply cost filters
        queryset = self._apply_cost_filters(queryset, params)

        # Custom ordering (handling dynamic 'cost' field)
        ordering = self._get_valid_ordering(params)
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset.select_related(
            "plan", "plan__subscription", "plan__subscription__category"
        )

    def _parse_and_validate_params(self, query_params):
        params = {}
        self._parse_category(params, query_params)
        self._parse_track_usage(params, query_params)
        self._parse_period(params, query_params)
        self._parse_cost_params(params, query_params)
        self._parse_date_filters(params, query_params)
        self._parse_ordering(params, query_params)
        return params

    def _parse_category(self, params, query_params):
        params["category_id"] = query_params.get("category_id")

    def _parse_track_usage(self, params, query_params):
        if track_usage := query_params.get("track_usage"):
            if track_usage.lower() not in ["true", "false"]:
                raise ValidationError("track_usage must be 'true' or 'false'")
            params["track_usage"] = track_usage.lower() == "true"

    def _parse_period(self, params, query_params):
        if period_str := query_params.get("period"):
            try:
                params["period"] = Plan.Period.get_days(period_str)
            except ValueError as e:
                raise ValidationError(str(e))

    def _parse_cost_params(self, params, query_params):
        for param in ["cost_min", "cost_max"]:
            if value := query_params.get(param):
                try:
                    params[param] = Decimal(value)
                except InvalidOperation:
                    raise ValidationError(f"{param} must be a decimal number")

    def _parse_date_filters(self, params, query_params):
        date_params = ["days_until_payment", "recently_paid"]
        for param in date_params:
            if value := query_params.get(param):
                try:
                    params[param] = int(value)
                    if params[param] < 0:
                        raise ValueError
                except ValueError:
                    raise ValidationError(f"{param} must be a positive integer")

    def _parse_ordering(self, params, query_params):
        if ordering := query_params.get("ordering"):
            allowed_static_fields = {"payment_date", "plan__name", "track_usage"}
            ordering_field = ordering.lstrip("-")

            if ordering_field not in allowed_static_fields and ordering_field != "cost":
                raise ValidationError(f"Invalid ordering field: {ordering_field}")

            if ordering_field == "cost" and not params.get("period"):
                raise ValidationError("Cannot order by 'cost' without a period parameter")

            params["ordering"] = ordering

    def _build_filters(self, params, today):
        filters = Q()
        self._apply_category_filter(filters, params)
        self._apply_track_usage_filter(filters, params)
        self._apply_payment_date_filters(filters, params, today)
        return filters

    def _apply_category_filter(self, filters, params):
        if category_id := params.get("category_id"):
            filters &= Q(plan__subscription__category__id=category_id)

    def _apply_track_usage_filter(self, filters, params):
        if track_usage := params.get("track_usage", None):
            filters &= Q(track_usage=track_usage)

    def _apply_payment_date_filters(self, filters, params, today):
        if days := params.get("days_until_payment"):
            end_date = today + timedelta(days=days)
            filters &= Q(payment_date__range=[today, end_date])

        if days := params.get("recently_paid"):
            start_date = today - timedelta(days=days)
            filters &= Q(payment_date__range=[start_date, today])

    def _annotate_cost(self, queryset, target_period):
        return queryset.annotate(
            cost=ExpressionWrapper(
                (F("plan__cost") * target_period)
                / Cast(F("plan__period"), DecimalField()),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )

    def _apply_cost_filters(self, queryset, params):
        if cost_min := params.get("cost_min"):
            queryset = queryset.filter(cost__gte=cost_min)
        if cost_max := params.get("cost_max"):
            queryset = queryset.filter(cost__lte=cost_max)
        return queryset

    def _get_valid_ordering(self, params):
        ordering = params.get("ordering")
        if not ordering:
            return None

        return ordering
    
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