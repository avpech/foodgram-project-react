from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Prefetch, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.filters import IngredientSearchFilter, RecipeFilter
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.utils import pdf_cart
from users.models import Subscribe

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для эндпоинта рецептов."""
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'head', 'options', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return (
                Recipe.objects.all().select_related('author')
                .prefetch_related(
                    'tags',
                    Prefetch(
                        'recipe_ingredients',
                        queryset=RecipeIngredient.objects.all(
                        ).select_related('ingredient')
                    ))
            )
        # Примечание. По поводу замечания серым цветом насчет того, что
        # запрос ниже сложный и его будет сложно дебажить.
        # Я просто ума не приложу, как его упростить :)
        # На данный момент запрос списка всех рецептов обходиться в пять
        # обращений к бд (плюс обращение по части авторизации).
        # И чтобы я из него ни убрал, количество обращений
        # вырастает кратно при большом количестве запрашиваемых объектов.
        return (
            Recipe.objects
            .add_is_favorited(self.request.user)
            .add_is_in_shopping_cart(self.request.user)
            .prefetch_related(
                'tags',
                Prefetch(
                    'recipe_ingredients',
                    queryset=RecipeIngredient.objects.all(
                    ).select_related('ingredient')
                ),
                Prefetch(
                    'author',
                    queryset=User.objects.annotate(
                        is_subscribed=Exists(Subscribe.objects.filter(
                            user=self.request.user,
                            author=OuterRef('pk')
                        ))
                    )
                )
            )
        )

    def _create_delete_obj(self, request, pk=None):
        if self.request.method == 'DELETE':
            obj = get_object_or_404(
                self.serializer_class.Meta.model,
                user=request.user, recipe=pk
            )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(Recipe, id=pk)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        ('post', 'delete'), detail=True,
        serializer_class=FavoriteSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранном."""
        return self._create_delete_obj(request, pk)

    @action(
        ('post', 'delete'), detail=True,
        serializer_class=ShoppingCartSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в списке покупок."""
        return self._create_delete_obj(request, pk)

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание pdf-файла со списком покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        return pdf_cart(ingredients)
