from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "recipe"

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet, basename="recipe")
router.register("tags", views.TagViewSet)
router.register("ingredients", views.IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("recipes/<int:pk>/", _, name="recipe-upload-image"),
]
