from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from core.models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    # Limit recipes to authenticated user
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)  # .order_by("-id")

    # Change serializer for list url
    def get_serializer_class(self):
        if self.action == "list":  # This means a list url with GET method
            return RecipeSerializer
        return super().get_serializer_class()

    # Set the field `user` = request.user by default when creating recipe instance
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
