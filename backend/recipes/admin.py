from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'followers_count'
    )
    search_fields = ('author__username', 'name')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInLine,)

    @admin.display(description='Добавлений в избранное')
    def followers_count(self, obj):
        return obj.followers.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit', 'name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
