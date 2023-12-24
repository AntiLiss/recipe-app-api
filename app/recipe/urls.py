from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "recipe"

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet, basename="recipe")
router.register('tags', views.TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("tags/", views.TagsAPIView.as_view(), name="tag-list"),
]