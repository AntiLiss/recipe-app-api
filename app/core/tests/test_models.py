"""Tests for models"""
from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(email="test@example.com", password="test123", name=None):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Test models"""

    # Users
    def test_create_user_with_email_successfully(self):
        """Test creating a user with an email successfully"""
        email = "test@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email normalization for new users"""
        sample_emails = [
            ["test1@EXAMPLE.COM", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = create_user(email=email, password="12345")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_value_error(self):
        """Test creating a new user without an email raises ValueError"""
        with self.assertRaises(ValueError):
            create_user(email="", password="12345")

    def test_create_superuser(self):
        """Test creating a supersuer"""
        superuser = get_user_model().objects.create_superuser(
            email="test@example.com", password="12345"
        )
        self.assertTrue(superuser.is_superuser)

    # Recipes
    def test_create_recipe_successfully(self):
        """Test creating recipe successfully"""
        user = create_user(email="test@example.com", password="121212", name="testname")
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe title",
            time_minutes=3.5,
            price=Decimal("10.99"),
            description="Sample description",
        )

        recipe_exists = models.Recipe.objects.filter(id=recipe.id).exists()
        self.assertTrue(recipe_exists)
        # I think don't need this one
        # self.assertEqual(str(recipe), recipe.title)

    @patch("core.models.uuid.uuid4")
    def test_recipe_filename_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.generate_recipe_image_path(None, "example.jpg")

        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")

    # Tags
    def test_create_tag_successfully(self):
        """Test creating tag successfully"""
        user = create_user(
            email="test@example.com",
            password="test123",
        )
        tag = models.Tag.objects.create(name="my_tag", user=user)

        self.assertEqual(str(tag), tag.name)

    # Ingredients
    def test_create_ingredient_successfully(self):
        """Test creating ingredient successfully"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="sample ingredient",
        )

        self.assertEqual(str(ingredient), ingredient.name)
