from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

import datetime
from .. import screentime, notifications

from ..models import User, UserPlan

class UpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        users = User.objects.filter(allow_notifications=True)

        today = datetime.datetime.today().date()

        for user in users:
            user_plans = UserPlan.objects.filter(user=user)

            for user_plan in user_plans:
                user_plan.update_payment_date()

                if user_plan.payment_date - today <= datetime.timedelta(days=3):
                    notifications.send_push_notification(
                        "Upcoming payment",
                        f"{user_plan.plan.subscription.name} is due at {user_plan.payment_date}",
                        user.id,
                    )

        return Response(
            {"message": "Subscription payments updated and notifications sent."},
            status=status.HTTP_200_OK,
        )


class UpdateUnusedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        users = User.objects.exclude(api_key_encrypted__isnull=True)

        for user in users:
            api_key = user.api_key_encrypted

            # Fetch active plans for the user
            user_plans = UserPlan.objects.filter(
                user=user, track_usage=True
            ).select_related("plan__subscription")

            # Fetch screen time data
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            end_date = datetime.date.today().isoformat()
            df = screentime.fetch_data(api_key, start_date, end_date)

            # Update usage scores
            for user_plan in user_plans:
                try:
                    subscription_name = user_plan.plan.subscription.name
                    user_plan.update_usage_score(subscription_name, df)
                except Exception as e:
                    print(f"Error processing {subscription_name}: {e}")

            # Send notifications for unused subscriptions
            if user.allow_notifications:
                unused_threshold = user.unused_threshold

                for user_plan in user_plans:
                    subscription_name = user_plan.plan.subscription.name

                    if user_plan.usage_score < unused_threshold:
                        notifications.send_push_notification(
                            "Unused Subscription",
                            f"The subscription '{subscription_name}' is unused.",
                            user.id,
                        )
                    # (Admin purposes) Display subscriptions after processing all user plans
                    screentime.display_subscriptions(subscription_name, df)

        return Response(
            {"message": "Subscription usage updated and notifications sent."},
            status=status.HTTP_200_OK,
        )
