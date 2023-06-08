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
        'get_author_email',
        'followers_count',
        'get_tags',
    )
    search_fields = ('author__username', 'author__email', 'name')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInLine,)

    @admin.display(description='Добавлений в избранное')
    def followers_count(self, obj):
        return obj.followers.count()

    @admin.display(ordering='author__email',
                   description='адрес электронной почты автора')
    def get_author_email(self, obj):
        return obj.author.email

    @admin.display(description='теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'get_email',
        'recipe',
        'get_tags',
    )
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_filter = ('recipe__tags',)

    @admin.display(ordering='user__email',
                   description='адрес электронной почты')
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description='теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.recipe.tags.all()])


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'get_email',
        'recipe',
        'get_tags',
    )
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_filter = ('recipe__tags',)

    @admin.display(ordering='user__email',
                   description='адрес электронной почты')
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description='теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.recipe.tags.all()])
