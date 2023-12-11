from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, AuthTokenSerializer


# Register user explicitly via APIView
class RegisterUserView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status.HTTP_400_BAD_REQUEST)


# Register user via generic view
# class RegisterUserView(generics.CreateAPIView):
#     serializer_class = UserSerializer


# Create token via DRF built-in ObtainAuthToken class
# class CreateTokenView(ObtainAuthToken):
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# Create token explicitly via APIView
class CreateTokenView(APIView):
    def post(self, request):
        token_serializer = AuthTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        user = token_serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status.HTTP_200_OK)
