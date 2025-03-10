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
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())

    class Meta:
        model = UserPlan
        fields = "__all__"
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user
        plan = data.get('plan')
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            raise serializers.ValidationError({"plan": "Plan already added to your subscriptions."})
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Handle annotated cost from view calculations
        annotated_cost = getattr(instance, "cost", None)
        representation["cost"] = annotated_cost if annotated_cost is not None else instance.plan.cost

        # Add plan-related information
        plan = instance.plan
        representation.update({
            "plan_id": plan.id,
            "plan_name": plan.name,
            "period": plan.get_period_display(),
            "free_trial": plan.free_trial
        })

        # Add subscription details
        subscription = plan.subscription
        representation.update({
            "subscription_id": subscription.id,
            "subscription_name": subscription.name,
            "category_id": subscription.category.id,
            "icon_url": subscription.icon_url
        })

        # Format user information
        representation["user"] = instance.user.username

        return representation

class PeriodQueryParamSerializer(serializers.Serializer):
    period = serializers.CharField(required=False)

    def validate_period(self, value):
        """Validate the period query parameter."""
        if value:
            try:
                period_days = Plan.Period.get_days(value)
                return period_days  # Return validated period
            except ValueError:
                valid_periods = [label for _, label in Plan.Period.choices]
                raise serializers.ValidationError(
                    f"Invalid period '{value}'. Valid options: {valid_periods}"
                )
        return None