from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        exclude = [
            "description",
            "user",  # Exclude user cuz it's user himself limited API
        ]
        read_only_fields = ["id"]


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        exclude = ["user"]
