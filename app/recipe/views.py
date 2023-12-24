from rest_framework import viewsets, mixins, generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from core.models import Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer


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

    # Set `user` = request.user by default
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    # Override deletion to return deleted tag in response
    def destroy(self, request, pk):
        tag = Tag.objects.get(id=pk)
        serializer = TagSerializer(instance=tag)
        # Need to access serializer.data cuz otherwise `id` == None
        foobar = serializer.data
        tag.delete()
        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)
