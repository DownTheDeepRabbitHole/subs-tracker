import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_URL = "https://api.onesignal.com"


def check_user_subscription(user_id):
    url = f"{ONESIGNAL_API_URL}/apps/{ONESIGNAL_APP_ID}/users/by/external_id/{user_id}"
    headers = {"Authorization": f"Basic {ONESIGNAL_API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        user_data = response.json()

        # Check if the user is subscribed
        return user_data.get("subscriptions", [{}])[0].get("notification_types") == 1
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user data for user {user_id}: {e}")
        return False


def send_push_notification(title, message, *user_ids):
    # Filter valid (subscribed) user IDs
    valid_user_ids = [str(user_id) for user_id in user_ids if check_user_subscription(user_id)]

    if not valid_user_ids:
        print("No subscribed users to send notifications to.")
        return

    # Prepare the notification payload
    url = f"{ONESIGNAL_API_URL}/notifications"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    data = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
        "include_external_user_ids": valid_user_ids,
        "target_channel": "push",
    }

    # Send the notification
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()

        if "errors" in response_data:
            print(f"Failed to send notification: {response_data['errors']}")
        else:
            print(f"Notification sent successfully: {response_data}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")