from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer,
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
        elif self.action == "upload_image":
            return RecipeImageSerializer
        return super().get_serializer_class()

    # Set the field `user` = request.user by default when creating recipe instance
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Extra action url to upload image to recipe
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class BaseRecipeAttrViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # Limit queryset to authenticated user
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("id")


# Tags
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()

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
class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients"""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def destroy(self, request, pk):
        """Delete item and return it in response"""
        ingredient = get_object_or_404(Ingredient, pk=pk)
        serializer = self.serializer_class(ingredient)
        data = serializer.data
        ingredient.delete()
        return Response(data, status.HTTP_204_NO_CONTENT)
