from rest_framework import serializers

from .models import User, Category, Subscription, Plan, UserPlan


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "allow_notifications",
            "api_key_encrypted",
            "advance_period",
            "unused_threshold",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    period = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = "__all__"

    def get_period(self, obj):
        return obj.get_period_display()


class SubscriptionSerializer(serializers.ModelSerializer):
    plans = PlanSerializer(many=True, required=False)

    class Meta:
        model = Subscription
        fields = "__all__"


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = "__all__"

    def get_cost(self, instance):
        # Check if cost is annotated (normalized in views)
        annotated_cost = getattr(instance, 'cost', None)
        if annotated_cost is not None:
            return annotated_cost
        else:
            return instance.plan.cost

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        annotated_cost = getattr(instance, "cost", None)

        if annotated_cost is not None:
            representation["cost"] = annotated_cost
        else:
            plan = instance.plan
            representation["cost"] = plan.cost

        plan = instance.plan
        subscription = plan.subscription

        representation["plan_name"] = plan.name
        representation["period"] = plan.get_period_display()
        representation["free_trial"] = plan.free_trial

        representation["subscription_name"] = subscription.name
        representation["category_id"] = subscription.category.id
        representation["icon_url"] = subscription.icon_url

        representation["user"] = instance.user.username
        representation["payment_date"] = instance.payment_date
        representation["last_updated"] = instance.last_updated
        representation["total_spent"] = instance.total_spent
        representation["track_usage"] = instance.track_usage
        representation["usage_score"] = instance.usage_score
        representation["average_usage"] = instance.average_usage

        return representation
