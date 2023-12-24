from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Create recipe with tags"""
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        # (Create) and assign tags separately
        if tags:
            user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=user, **tag)
            recipe.tags.add(tag_obj)
        # .add() auto saves changes, so no need to call .save()
        return recipe

    def update(self, instance, validated_data):
        """Update recipe with tags"""
        tags = validated_data.pop("tags", None)
        super().update(instance, validated_data)
        # (Create) and assign tags separately
        # Check is there even `tags` field in validated_data
        if tags is not None:
            user = self.context["request"].user
            # .clear() auto saves changes, so no need to call .save()
            instance.tags.clear()
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(user=user, **tag)
                instance.tags.add(tag_obj)
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
