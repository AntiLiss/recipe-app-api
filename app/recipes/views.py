from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)  # .order_by("-id")

    def get_serializer_class(self):
        if self.kwargs.get("pk"):
            return RecipeDetailSerializer
        return super().get_serializer_class()

    # Almost the same
    # def get_serializer_class(self):
    #     if self.action == 'list':
    #         return RecipeSerializer
    #     return self.serializer_class
