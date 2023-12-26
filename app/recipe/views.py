from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
)


# Recipes
class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    # Limit recipes to authenticated user
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("id")

    # Change serializer for list url
    def get_serializer_class(self):
        if self.action == "list":  # This means a list url with GET method
            return RecipeSerializer
        return super().get_serializer_class()

    # Set the field `user` = request.user by default when creating recipe instance
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Tags
class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    # Limit tags to authenticated user
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("id")

    # Override deletion to return deleted tag in response
    def destroy(self, request, pk):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(instance=tag)
        # Need to access serializer.data before tag delete
        # cuz otherwise `id` == None
        data = serializer.data
        tag.delete()
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


# Ingredients
class IngredientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("id")

    def destroy(self, request, pk):
        """Delete item and return it in response"""
        ingredient = get_object_or_404(Ingredient, pk=pk)
        serializer = self.serializer_class(ingredient)
        data = serializer.data
        ingredient.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)
