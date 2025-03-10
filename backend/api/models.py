from django.contrib.auth.models import AbstractUser
from django.db import models

from . import screentime
from datetime import date, timedelta

from . import utils


class User(AbstractUser):
    USAGE_SCORE_CHOICES = [(i, i) for i in range(0, 11)]

    remember_me = models.BooleanField(default=False)
    allow_notifications = models.BooleanField(default=False)
    api_key_encrypted = models.CharField(max_length=255, blank=True, null=True)
    advance_period = models.IntegerField(default=3)
    unused_threshold = models.IntegerField(default=3, choices=USAGE_SCORE_CHOICES)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_emoji = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


# Shared subscription table
class Subscription(models.Model):
    name = models.CharField(max_length=100)
    icon_url = models.URLField(
        default="https://icons.veryicon.com/png/o/business/settlement-platform-icon/default-16.png"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subscriptions"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.icon_url = utils.get_icon_url(self.name)
        super().save(*args, **kwargs)


class Plan(models.Model):
    class Period(models.IntegerChoices):
        DAY = 1, "day"
        WEEK = 7, "week"
        MONTH = 30, "month"
        QUARTER = 90, "quarter"
        YEAR = 365, "year"

        @classmethod
        def get_days(cls, period_str):
            period_str = period_str.strip().lower()
            for value, label in cls.choices:
                if label.lower() == period_str:
                    return value
            raise ValueError(
                f"Invalid period string: {period_str}. Valid options: {[label for _, label in cls.choices]}"
            )

        @classmethod
        def get_label(cls, days):
            for value, label in cls.choices:
                if value == days:
                    return label
            raise ValueError(
                f"Invalid period value: {days}. Valid options: {[value for value, _ in cls.choices]}"
            )

    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="plans"
    )
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.IntegerField(choices=Period.choices, default=Period.MONTH)
    free_trial = models.BooleanField(default=False)

    def cost_per_period(self, target_period):
        return (self.cost / self.period) * target_period

    def __str__(self):
        return f"{self.name} - {self.subscription.name}"


class UserPlan(models.Model):
    USAGE_SCORE_CHOICES = [(i, i) for i in range(0, 11)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_plans")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    payment_date = models.DateField()
    last_updated = models.DateField(null=True, blank=True)
    total_spent = models.IntegerField(default=0)
    
    track_usage = models.BooleanField(default=False)
    usage_score = models.IntegerField(default=1, choices=USAGE_SCORE_CHOICES)
    average_usage = models.IntegerField(default=0)

    def update_payment_date(self):
        today = date.today()

        if self.payment_date < today:
            if self.plan.free_trial:
                return

            if not self.plan.period:
                raise ValueError("Period must be set for the plan.")

            self.payment_date += timedelta(days=self.plan.period)
            self.total_spent += self.plan.cost
            self.last_updated = today

            self.save()

    def update_usage_score(self, subscription_name, df):
        self.usage_score = screentime.calculate_usage(subscription_name, df)
        self.save()

    def __str__(self):
        return f"{self.user.username}'s {self.plan.subscription.name} - {self.plan.name}"
    
    class Meta:
        ordering = ['plan__name']
