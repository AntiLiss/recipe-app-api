import tempfile
import os
from decimal import Decimal
from PIL import Image
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from .test_tag_api import create_tag
from .test_ingredient_api import create_ingredient


RECIPE_LIST_URL = reverse("recipe:recipe-list")


def get_detail_url(recipe_id):
    return reverse("recipe:recipe-detail", kwargs={"pk": recipe_id})


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


def get_image_upload_url(recipe_id):
    """Create and return image upload url"""
    return reverse("recipe:recipe-upload-image", kwargs={"pk": recipe_id})


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
        recipes = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipes.exists())
        recipe = recipes[0]
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
            tag_obj = Tag.objects.filter(
                user=self.user,
                **tag,
            )
            self.assertTrue(tag_obj.exists())
            self.assertIn(tag_obj[0], recipe.tags.all())

    def test_create_recipe_with_existing_tag(self):
        """Test creating recipe with already existing tag"""
        tag_dinner = create_tag(user=self.user, name="dinner")
        payload = {
            "title": "sample title",
            "time_minutes": Decimal("7.5"),
            "price": Decimal("199.99"),
            "tags": [
                {"name": "dinner"},  # this must use `tag_dinner`
            ],
        }
        res = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipes.exists())
        recipe = recipes[0]
        # Assert exactly `tag_dinner` was assigned
        self.assertIn(tag_dinner, recipe.tags.all())
        self.assertEqual(recipe.tags.count(), len(payload["tags"]))
        tag_dinner_count = Tag.objects.filter(
            user=self.user,
            name=tag_dinner.name,
        ).count()
        # Assert no recreation of existing tag
        self.assertEqual(tag_dinner_count, 1)

    def test_create_new_tags_on_update(self):
        """Test create and assign new tags when updating recipe"""
        recipe = create_recipe(user=self.user)
        payload = {
            "tags": [{"name": "italian"}, {"name": "pizza"}],
        }
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for tag in payload["tags"]:
            added_tags = Tag.objects.filter(user=self.user, **tag)
            self.assertTrue(added_tags.exists())
            added_tag = added_tags[0]
            self.assertIn(added_tag, recipe.tags.all())

    def test_assign_existing_tag_on_update(self):
        """Test assign already existing tag when updating recipe"""
        tag_lunch = create_tag(user=self.user, name="lunch")
        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"name": "lunch"}]}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        tag_lunch_count = Tag.objects.filter(
            user=self.user,
            name=tag_lunch.name,
        ).count()
        self.assertEqual(tag_lunch_count, 1)

    def test_reassign_recipe_tags_on_update(self):
        """Test reassigning tags when recipe update"""
        original_tag = create_tag(user=self.user, name="original tag")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(original_tag)

        new_tag = create_tag(user=self.user, name="new tag")
        payload = {"tags": [{"name": "new tag"}]}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # We've reassigned `tags` field, so now recipe.tags must include
        # only tag from payload
        self.assertEqual(recipe.tags.count(), 1)
        self.assertNotIn(original_tag, recipe.tags.all())
        self.assertIn(new_tag, recipe.tags.all())
        new_tag_count = Tag.objects.filter(
            user=self.user,
            name=new_tag.name,
        ).count()
        self.assertEqual(new_tag_count, 1)

    def test_clear_recipe_tags(self):
        """Test removing recipe tags when recipe update"""
        tag = create_tag(user=self.user, name="sample tag")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {"tags": []}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating recipe with new ingredients"""
        payload = {
            "title": "sample title",
            "time_minutes": Decimal(7.5),
            "price": Decimal("199.99"),
            "ingredients": [
                {"name": "carrot"},
                {"name": "tomato"},
            ],
        }
        res = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipe.exists())
        self.assertEqual(
            recipe[0].ingredients.count(),
            len(payload["ingredients"]),
        )
        for ing in payload["ingredients"]:
            ingredient = Ingredient.objects.filter(user=self.user, **ing)
            self.assertTrue(ingredient.exists())
            self.assertIn(ingredient[0], recipe[0].ingredients.all())

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating recipe with already existing ingredient"""
        ingredient_carrot = create_ingredient(
            user=self.user,
            name="carrot",
        )
        payload = {
            "title": "sample title",
            "time_minutes": Decimal(7.5),
            "price": Decimal("199.99"),
            "ingredients": [{"name": "carrot"}],
        }
        res = self.client.post(RECIPE_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(id=res.data["id"])
        self.assertTrue(recipe.exists())
        self.assertEqual(recipe[0].ingredients.count(), 1)
        self.assertIn(ingredient_carrot, recipe[0].ingredients.all())
        ingredients = Ingredient.objects.filter(
            user=self.user,
            name=ingredient_carrot.name,
        )
        self.assertEqual(ingredients.count(), 1)

    def test_create_new_ingredients_on_update(self):
        """Test creating and setting ingredients when recipe update"""
        recipe = create_recipe(user=self.user)
        payload = {"ingredients": [{"name": "potato"}]}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 1)
        for ing in payload["ingredients"]:
            ing_obj = Ingredient.objects.filter(user=self.user, **ing)
            self.assertTrue(ing_obj.exists())
            self.assertIn(ing_obj[0], recipe.ingredients.all())

    def test_assign_existing_ingredients_on_update(self):
        """Test setting already existing ingredient when recipe update"""
        recipe = create_recipe(user=self.user)
        ingredient_tomato = create_ingredient(user=self.user, name="tomato")
        payload = {"ingredients": [{"name": "tomato"}]}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertIn(ingredient_tomato, recipe.ingredients.all())
        ingredient_tomato_count = Ingredient.objects.filter(
            user=self.user,
            name=ingredient_tomato.name,
        ).count()
        self.assertEqual(ingredient_tomato_count, 1)

    def test_clear_ingredients(self):
        """Test removing all ingredients when recipe update"""
        ingredient_1 = create_ingredient(user=self.user)
        ingredient_2 = create_ingredient(user=self.user)
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_1, ingredient_2)

        payload = {"ingredients": []}
        url = get_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTests(TestCase):
    """Test for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="121212",
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(user=self.user)

    # TODO Check is this necessary
    # def tearDown(self):
    #     self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading image to recipe"""
        url = get_image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)

            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = get_image_upload_url(self.recipe.id)
        payload = {"image": "not image"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
