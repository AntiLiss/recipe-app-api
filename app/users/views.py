from django.contrib.auth import authenticate
from rest_framework import generics, authentication, permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, AuthTokenSerializer
from core.models import User


# Register user explicitly via APIView
class RegisterUserView(APIView):
    serizalizer_class = UserSerializer

    def post(self, request):
        user_serializer = self.serizalizer_class(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data, status.HTTP_201_CREATED)


# The same via generic view
class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


# Create token explicitly via APIView
class CreateTokenView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        token_serializer = self.serializer_class(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        user = token_serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status.HTTP_200_OK)


# The same via DRF built-in ObtainAuthToken class
# class CreateTokenView(ObtainAuthToken):
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# Retrieve and update user profile explicitly via APIView
class ManageUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        user_serializer = self.serializer_class(instance=user)
        return Response(user_serializer.data, status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        user_serializer = self.serializer_class(
            instance=user, data=request.data, partial=True
        )
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data, status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        user_serializer = self.serializer_class(instance=user, data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data, status.HTTP_200_OK)


# The same via generic view
# class ManageUserView(generics.RetrieveUpdateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [authentication.TokenAuthentication]
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user
