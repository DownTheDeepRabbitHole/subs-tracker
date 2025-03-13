from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User, Category, Subscription, Plan, UserPlan


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        raise serializers.ValidationError("Incorrect credentials")
    
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {"password":{"write_only":True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "avatar_url"]


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


class PeriodField(serializers.Field):
    def to_internal_value(self, data):
        try:
            return Plan.Period.get_days(data)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def to_representation(self, value):
        return Plan.Period.get_label(value)


class PeriodQueryParamSerializer(serializers.Serializer):
    period = serializers.CharField(required=False)

    def validate_period(self, value):
        if value:
            try:
                period_days = Plan.Period.get_days(value)
                return period_days
            except ValueError:
                valid_periods = [label for _, label in Plan.Period.choices]
                raise serializers.ValidationError(
                    f"Invalid period '{value}'. Valid options: {valid_periods}"
                )
        return None


class PlanSerializer(serializers.ModelSerializer):
    period = PeriodField()

    class Meta:
        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    plans = PlanSerializer(many=True, required=False)

    class Meta:
        model = Subscription
        fields = "__all__"


class UserPlanSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(source="plan.id", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    period = PeriodField(source="plan.period", read_only=True)
    free_trial = serializers.BooleanField(source="plan.free_trial", read_only=True)

    subscription_id = serializers.IntegerField(
        source="plan.subscription.id", read_only=True
    )
    subscription_name = serializers.CharField(
        source="plan.subscription.name", read_only=True
    )
    icon_url = serializers.URLField(source="plan.subscription.icon_url", read_only=True)
    category_id = serializers.IntegerField(
        source="plan.subscription.category.id", read_only=True
    )

    class Meta:
        model = UserPlan
        fields = "__all__"
        read_only_fields = ("user",)

    def validate(self, data):
        user = self.context["request"].user
        plan = data.get("plan")
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            raise serializers.ValidationError(
                {"plan": "Plan already added to your subscriptions."}
            )
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Handle annotated cost from view calculations
        annotated_cost = getattr(instance, "cost", None)
        representation["cost"] = (
            annotated_cost if annotated_cost is not None else instance.plan.cost
        )

        # Format user information
        representation["user"] = instance.user.username

        return representation
