from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer


class RegisterUserView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status.HTTP_400_BAD_REQUEST)


# class RegisterUserView(generics.CreateAPIView):
#     serializer_class = UserSerializer
