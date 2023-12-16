from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("users:register")
TOKEN_URL = reverse("users:token")
ME_URL = reverse("users:me")


def create_user(**fields):
    user = get_user_model().objects.create_user(**fields)
    return user


class PublicUserAPITests(TestCase):
    """Test the public features of the User API"""

    def setUp(self):
        """Set up test class attributes"""
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            "email": "test@example.com",
            "password": "123456",
            "name": "testname",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_already_exists_error(self):
        payload = {
            "email": "test@example.com",
            "password": "123456",
            "name": "Test name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload = {
            "email": "test@example.com",
            "password": "12",
            "name": "Test name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_generate_user_token(self):
        user_credentials = {
            "email": "test@example.com",
            "password": "123456",
            "name": "Test name",
        }
        create_user(**user_credentials)
        payload = {
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_generate_token_wrong_credentials(self):
        user_credentials = {
            "email": "test@example.com",
            "password": "123456",
            "name": "Test name",
        }
        create_user(**user_credentials)
        wrong_payload = {
            "email": user_credentials["email"],
            "password": "wrongpassword",
        }
        res = self.client.post(TOKEN_URL, wrong_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_generate_token_blank_password(self):
        wrong_payload = {
            "email": "test@example.com",
            "password": "",
        }
        res = self.client.post(TOKEN_URL, wrong_payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com", password="123456", name="Testname"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"email": self.user.email, "name": self.user.name})

    def test_me_post_not_allowed(self):
        """Test post method not allowed on me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test updating profile for the authenticated user"""
        payload = {
            "email": "foobar@example.com",
            "password": "updatedpass",
            "name": "updatedname",
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
