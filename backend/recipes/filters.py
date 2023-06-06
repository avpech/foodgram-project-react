from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


# Примечание. Предыдущий поиск убрал, но так и не смог разобраться,
# как ту задачу было проще сделать. Если просто указать во вьюсете
# search_fields = ('^name', 'name'), то поиск хоть и работает, но
# сортировка результатов не та - нужна ведь такая сортировка, чтобы вначале
# отобразились результаты по вхождению в начало названия, а уже после них
# по вхождению в произвольном месте (именно так предложили сделать
# в теории практикума в качестве усложнения). Может я чего-то совсем
# очевидного не замечаю, но поскольку дедлайн уже близко, то решил уже
# не тратить время и сделать просто по вхождению в начало названия :)
#
class IngredientSearchFilter(SearchFilter):
    """Поиск ингредиентов."""
    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтры для страницы рецептов."""
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация находящихся в избранном рецептов."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(followers__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация находящихся в списке покупок рецептов."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset
