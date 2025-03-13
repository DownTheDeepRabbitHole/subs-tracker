from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class TokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Retrieve the access token from the HTTPOnly cookie
        access_token = request.COOKIES.get("access_token")

        if access_token:
            try:
                access = AccessToken(access_token)

                # Check if the access token is about to expire
                if datetime.now() > datetime.fromtimestamp(access["exp"]) - timedelta(
                    minutes=10
                ):
                    # About to expire: attempt a refresh
                    refresh_token = request.COOKIES.get("refresh_token")

                    if refresh_token:
                        refresh = RefreshToken(refresh_token)
                        new_access_token = str(refresh.access_token)

                        # Proceeds with the rest of the response
                        response = self.get_response(request)

                        response.set_cookie(
                            key="access_token",
                            value=new_access_token,
                            httponly=True,
                            secure=True,
                            samesite="None",
                        )

                        response.set_cookie(
                            key="refresh_token",
                            value=str(refresh),
                            httponly=True,
                            secure=True,
                            samesite="None",
                        )
                        return response
            except Exception as e:
                pass  # Graceful handling of invalid/expired tokens

        return self.get_response(request)
