from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, 'tags')
router.register(r'recipes', RecipeViewSet, 'recipes')
router.register(r'ingredients', IngredientViewSet, 'ingredients')
router.register(r'users', CustomUserViewSet, 'users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
