from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..serializers import UserSettingsSerializer

class UserSettingsView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSettingsSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSettingsSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class GetUserId(APIView):
    def get(self, request):
        return Response({"user_id": request.user.id}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Both username and password must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "A user with that username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(username=username, password=password)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )