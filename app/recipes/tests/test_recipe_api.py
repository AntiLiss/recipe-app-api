from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe
from recipes.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_LIST_URL = reverse("recipes:recipe-list")


def get_detail_url(recipe_id):
    return reverse("recipes:recipe-detail", kwargs={"pk": recipe_id})


def create_recipe(user, **fields):
    default_fields = {
        "title": "sample title",
        "time_minutes": Decimal(7.5),
        "price": Decimal("199.99"),
        "description": "sample description",
        "link": "www.example.com",
    }
    default_fields.update(**fields)

    return Recipe.objects.create(user=user, **default_fields)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authorization is required to call API"""
        res = self.client.get(RECIPE_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="121212",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_recipes(self):
        """Test listing recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_LIST_URL)
        recipes = Recipe.objects.all()  # .order_by("-id")
        recipe_serializer = RecipeSerializer(instance=recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test if the list of recipes is limited to authenticated user"""
        other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="121212",
        )
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=other_user)

        res = self.client.get(RECIPE_LIST_URL)
        recipes = Recipe.objects.filter(user=self.user)  # .order_by("-id")
        recipe_serializer = RecipeSerializer(instance=recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_serializer.data)

    def test_retrieve_recipe_detail(self):
        """Test retrieving specific recipe"""
        recipe = create_recipe(user=self.user)
        url = get_detail_url(recipe.id)
        res = self.client.get(url)

        recipe_serializer = RecipeDetailSerializer(instance=recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_serializer.data)
