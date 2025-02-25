from rest_framework import serializers

from .models import Category, Subscription, Plan, UserPlan


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    plans = PlanSerializer(many=True)

    class Meta:
        model = Subscription
        fields = "__all__"

class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = "__all__"

    # Flatten the 'plan' and 'subscription' into top-level fields
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        plan_data = PlanSerializer(instance.plan).data
        
        subscription_id = plan_data.get('subscription')
        subscription_data = Subscription.objects.filter(id=subscription_id).first()
        
        
        representation['plan_name'] = plan_data.get('name', '')
        representation['cost'] = plan_data.get('cost', 0)
        representation['period'] = plan_data.get('period', '')
        representation['free_trial'] = plan_data.get('free_trial', False)

        representation['subscription_name'] = subscription_data.name
        representation['category_id'] = subscription_data.category.id
        representation['icon_url'] = subscription_data.icon_url


        representation['user'] = instance.user.username
        representation['payment_date'] = instance.payment_date
        representation['last_updated'] = instance.last_updated
        representation['total_spent'] = instance.total_spent
        representation['track_usage'] = instance.track_usage
        representation['usage_score'] = instance.usage_score
        representation['average_usage'] = instance.average_usage
        
        return representation