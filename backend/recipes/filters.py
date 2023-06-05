from django.db.models import F, Value
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class IngredientFilter(FilterSet):
    """Поиск ингредиентов."""
    name = filters.CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        return (queryset.filter(name__istartswith=value)
                .alias(order=Value(0)).annotate(order=F('order'))
                .union(queryset.filter(name__icontains=value)
                       .exclude(name__istartswith=value)
                       .alias(order=Value(1)).annotate(order=F('order')))
                .order_by('order'))


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
