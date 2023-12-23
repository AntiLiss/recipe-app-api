from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipes.serializers import TagSerializer

TAG_LIST_URL = reverse("recipes:tag-list")


def get_detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse("recipes:tag-detail", kwargs={"pk": tag_id})


def create_tag(user, **fields):
    default_fields = {"name": "testname"}
    default_fields.update(**fields)
    return Tag.objects.create(user=user, **default_fields)


def create_user(email="test@example.com", password="test123"):
    return get_user_model().objects.create_user(email, password)


class PublicTagAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        """Test authorization is required to call API"""
        res = self.client.get(TAG_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # def test_create_tag(self):
    #     payload = {"name": "mytag"}
    #     res = self.client.post(TAG_LIST_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     tag = Tag.objects.get(id=res.data["id"])
    #     self.assertEqual(tag.name, payload["name"])
    #     self.assertEqual(tag.user, self.user)

    def test_retrieve_tag(self):
        """Test retrieving a tag"""
        tag = create_tag(user=self.user)
        url = get_detail_url(tag.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag_serializer = TagSerializer(instance=tag)
        self.assertEqual(res.data, tag_serializer.data)

    def test_list_tags(self):
        """Test listing tags"""
        create_tag(user=self.user)
        create_tag(user=self.user)
        create_tag(user=self.user)

        res = self.client.get(TAG_LIST_URL)
        tags = Tag.objects.all().order_by("id")
        tag_serializer = TagSerializer(instance=tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, tag_serializer.data)

    def test_tag_list_limited_to_user(self):
        """Test if the list of tags are limited to authenticated user"""
        other_user = create_user(
            email="other@example.com",
            password="test123",
        )
        create_tag(user=self.user)
        create_tag(user=other_user)

        res = self.client.get(TAG_LIST_URL)
        tags = Tag.objects.filter(user=self.user)
        tag_serializer = TagSerializer(instance=tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, tag_serializer.data)

    def test_partial_update_tag(self):
        """Test partial update of tag"""
        tag = create_tag(user=self.user)
        url = get_detail_url(tag.id)
        payload = {"name": "updated name"}
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        tag = create_tag(user=self.user)
        url = get_detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tag_exists = Tag.objects.filter(id=tag.id).exists()
        self.assertFalse(tag_exists)
        tag_serializer = TagSerializer(instance=tag)
        self.assertEqual(res.data, tag_serializer.data)
