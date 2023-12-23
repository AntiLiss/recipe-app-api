from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag
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

    def test_authorization_required(self):
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
        recipes = Recipe.objects.all().order_by("id")
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
        recipes = Recipe.objects.filter(user=self.user).order_by("id")
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

    def test_create_recipe(self):
        "Test recipe created successfully"
        payload = {
            "title": "sample title",
            "time_minutes": Decimal(7.5),
            "price": Decimal("199.99"),
            "description": "sample description",
        }
        res = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test recipe partial update successfully"""
        original_price = Decimal("100.99")
        recipe = create_recipe(user=self.user, price=original_price)
        payload = {
            "title": "new title",
            "description": "new description",
        }
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.price, original_price)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test recipe entire update"""
        recipe = create_recipe(user=self.user)
        payload = {
            "description": "new description",
        }
        url = get_detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        # Asserting partial payload raises error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        for k, v in payload.items():
            self.assertNotEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test recipe deleting"""
        recipe = create_recipe(user=self.user)
        url = get_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        recipe_exists = Recipe.objects.filter(id=recipe.id).exists()
        self.assertFalse(recipe_exists)

    def test_delete_other_user_recipe_error(self):
        """Test deleting other user's recipe gives error"""
        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com",
            password="test123",
            name="otheruser",
        )
        recipe = create_recipe(user=other_user)
        url = get_detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating recipe with new tags"""
        payload = {
            "title": "sample title",
            "time_minutes": Decimal("7.5"),
            "price": Decimal("199.99"),
            "tags": [{"name": "tag1"}, {"name": "tag2"}],
        }
        res = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipes.exists())
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), len(payload["tags"]))
        for tag in payload["tags"]:
            tag_exists = Tag.objects.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(tag_exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating recipe with already existing tags"""
        tag_dinner = Tag.objects.create(name="dinner", user=self.user)
        payload = {
            "title": "sample title",
            "time_minutes": Decimal("7.5"),
            "price": Decimal("199.99"),
            "tags": [{"name": "dinner"}, {"name": "georgian"}],
        }
        res = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipes.exists())
        recipe = recipes[0]
        self.assertIn(tag_dinner, recipe.tags.all())
        self.assertEqual(recipe.tags.count(), len(payload["tags"]))
        for tag in payload["tags"]:
            tag_count = Tag.objects.filter(
                name=tag["name"],
                user=self.user,
            ).count()
            # Assert no recreation of existing tag
            self.assertTrue(tag_count, 1)
