from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient
from rest_framework.serializers import Serializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "ingredients"]

    def _assign_tags(self, tags, recipe):
        """Get or create and then assign tags to recipe"""
        user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=user, **tag)
            recipe.tags.add(tag_obj)

    def _assign_ingredients(self, ingredients, recipe):
        """Get or create and then assign ingredients to recipe"""
        user = self.context["request"].user
        for ing in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(user=user, **ing)
            recipe.ingredients.add(ing_obj)

    def create(self, validated_data):
        """Create recipe with tags"""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        # (Create) and assign tags and ingredients separately
        self._assign_tags(tags, recipe)
        self._assign_ingredients(ingredients, recipe)
        # .add() auto saves changes, so no need to call .save()
        return recipe

    def update(self, instance, validated_data):
        """Update recipe with tags"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        super().update(instance, validated_data)
        # Check is there even `tags` field in validated_data
        if tags is not None:
            # .clear() auto saves changes, so no need to call .save()
            instance.tags.clear()
            self._assign_tags(tags, instance)

        # Check is there even `ingredients` field in validated_data
        if ingredients is not None:
            instance.ingredients.clear()
            self._assign_ingredients(ingredients, instance)

        return instance
