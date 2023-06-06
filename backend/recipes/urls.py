from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, 'tags')
router.register(r'recipes', RecipeViewSet, 'recipes')
router.register(r'ingredients', IngredientViewSet, 'ingredients')

urlpatterns = [
    path('api/', include(router.urls)),
]
