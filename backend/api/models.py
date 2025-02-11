from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    remember_me = models.BooleanField(default=False)
    allow_notifications = models.BooleanField(default=False)
    api_key_encrypted = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Shared subscription table
class Subscription(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subscriptions"
    )

    def __str__(self):
        return self.name


# Shared payment plans table
class Plan(models.Model):
    PERIOD_CHOICES = [
        ("month", "Month"),
        ("year", "Year"),
        ("week", "Week"),
    ]

    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="plans"
    )
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=50, choices=PERIOD_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.subscription.name}"


# User-specific subscriptions
class UserPlan(models.Model):
    USAGE_SCORE_CHOICES = [(i, i) for i in range(0, 11)]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_plans"
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    next_payment_date = models.DateField(null=True, blank=True)
    last_updated = models.DateField(null=True, blank=True)
    track_usage = models.BooleanField(default=False)
    usage_score = models.IntegerField(default=0, choices=USAGE_SCORE_CHOICES)
    average_usage = models.IntegerField(default=0)

    def __str__(self):
        return (
            f"{self.user.username}'s {self.plan.subscription.name} - {self.plan.name}"
        )