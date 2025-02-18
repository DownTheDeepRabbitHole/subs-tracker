from rest_framework import serializers

from .models import Category, Subscription, Plan, UserPlan


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class PlanSerializerwithSubs(serializers.ModelSerializer):
    subscription = SubscriptionSerializer()

    class Meta:
        model = Plan
        fields = "__all__"


class UserPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializerwithSubs()

    class Meta:
        model = UserPlan
        fields = "__all__"
