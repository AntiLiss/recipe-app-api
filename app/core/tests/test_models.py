"""Tests for models"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successfully(self):
        """Test creating a user with an email successfully"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)
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
            user = get_user_model().objects.create_user(email=email, password="12345")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_value_error(self):
        """Test creating a new user without an email raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="12345")

    def test_create_superuser(self):
        """Test creating a supersuer"""
        superuser = get_user_model().objects.create_superuser(
            email="test@example.com", password="12345"
        )
        self.assertTrue(superuser.is_superuser)
