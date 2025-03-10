from datetime import date, timedelta

from decimal import Decimal
from django.db.models import DecimalField, ExpressionWrapper, F, Avg
from django.db.models.functions import Coalesce
from django.utils import timezone


class SpendingCalculator:
    """Calculating subscription spending statistics."""

    DEFAULT_PERIODS = [
        ("day", 1),
        ("week", 7),
        ("month", 30),
        ("quarter", 90),
        ("year", 365),
    ]

    def __init__(self, user_plans):
        self.user_plans = user_plans.select_related("plan")

    def calculate_spending(self, periods):
        """Calculates total spending over each of the time periods."""
        end_date = timezone.localdate()
        results = {}

        for period_name, days in periods:
            start_date = end_date - timedelta(days=days)
            total = self._calculate_range_spending(start_date, end_date)
            results[period_name] = round(total, 2)

        return results

    def calculate_custom_spending(self, days):
        """Calculate spending over a custom time period (__ days)"""
        end_date = timezone.localdate()
        start_date = end_date - timedelta(days=days)
        return round(self._calculate_range_spending(start_date, end_date), 2)

    def _calculate_range_spending(self, start_date, end_date):
        """Calculates the spending within a range"""
        total = 0.0

        for user_plan in self.user_plans:
            plan = user_plan.plan
            if plan.period <= 0:
                continue

            payment_date = user_plan.payment_date
            if payment_date > end_date:
                payment_date = self._adjust_payment_date(
                    payment_date, end_date, plan.period
                )

            if payment_date < start_date:
                continue

            num_payments = self._count_payments_in_range(
                payment_date, start_date, plan.period
            )
            total += num_payments * float(plan.cost)

        return total

    def _adjust_payment_date(self, current_date, end_date, period):
        """Find the first payment date <= end date"""
        days_over = (current_date - end_date).days
        periods_over = (days_over + period - 1) // period # Rounds it essentially
        return current_date - timedelta(days=periods_over * period)

    def _count_payments_in_range(self, last_payment, start_date, period):
        """Calculate number of payments between start_date and last_payment"""
        days_in_range = (last_payment - start_date).days
        if days_in_range < 0:
            return 0
        return (days_in_range // period) + 1


class AverageSpendingCalculator:
    """Calculating average (normalized) spending statistics"""

    def __init__(self, user_plans):
        self.queryset = user_plans.select_related("plan").only(
            "plan__cost", "plan__period"
        )

    def calculate_averages(self, periods):
        """Calculate normalized averages for multiple periods"""
        results = {}

        for period_days, period_label in periods:
            avg = self._calculate_normalized_average(period_days)
            results[period_label] = round(avg, 2)

        return results

    def _calculate_normalized_average(self, period_days: int) -> float:
        """Core calculation for a single period"""
        queryset = self.queryset.annotate(
            normalized_cost=ExpressionWrapper(
                F("plan__cost") * period_days / F("plan__period"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )

        aggregate = queryset.aggregate(
            average=Coalesce(Avg("normalized_cost"), Decimal(0))
        )

        return float(aggregate["average"])
