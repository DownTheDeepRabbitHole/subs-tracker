from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class TokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Retrieve the access token from the HTTPOnly cookie
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        remember_me = request.COOKIES.get("remember_me") == "True"

        if not (remember_me and access_token and refresh_token):
            return response

        try:
            # Parse the access token and check expiration
            access = AccessToken(access_token)
            token_expiry = datetime.fromtimestamp(access["exp"])

            # Check if token is about to expire
            if datetime.now() > token_expiry - timedelta(minutes=10):
                # Refresh the token
                refresh = RefreshToken(refresh_token)
                new_access = refresh.access_token

                response.set_cookie(
                    key="access_token",
                    value=str(new_access),
                    httponly=True,
                    secure=True,
                    samesite="None",
                    max_age=new_access.lifetime,
                )

                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite="None",
                    max_age=refresh.lifetime,
                )
        except Exception as e:
            pass

        return response
