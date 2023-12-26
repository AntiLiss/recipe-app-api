from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer
from .test_tag_api import create_user

INGREDIENT_LIST_URL = reverse("recipe:ingredient-list")


def get_detail_url(ingredient_id):
    """Get detail url for ingredient"""
    return reverse("recipe:ingredient-detail", kwargs={"pk": ingredient_id})


def create_ingredient(user, name="sample ingredient"):
    return Ingredient.objects.create(user=user, name=name)


class PublicIngredientAPITests(TestCase):
    """Test for unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        """Test authorizations required to deal with api"""
        res = self.client.get(INGREDIENT_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient(self):
        """Test specific ingredient retrieving"""
        ingredient = create_ingredient(user=self.user)
        url = get_detail_url(ingredient.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = IngredientSerializer(instance=ingredient)
        self.assertEqual(res.data, serializer.data)

    def test_list_ingredients(self):
        """Test ingredients listing"""
        create_ingredient(user=self.user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENT_LIST_URL)
        ingredients = Ingredient.objects.all().order_by("id")
        serializer = IngredientSerializer(instance=ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test if indredients are limited to authenticated user"""
        other_user = create_user(email="other_user@example.com")
        create_ingredient(user=other_user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENT_LIST_URL)
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(instance=ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test ingredient updating"""
        ingredient = create_ingredient(user=self.user)
        url = get_detail_url(ingredient.id)
        payload = {"name": "new name"}
        res = self.client.patch(url, payload)

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test ingredient deleting"""
        ingredient = create_ingredient(user=self.user)
        url = get_detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient_exists = Ingredient.objects.filter(id=ingredient.id).exists()
        self.assertFalse(ingredient_exists)
        serializer = IngredientSerializer(ingredient)
        self.assertEqual(res.data, serializer.data)
