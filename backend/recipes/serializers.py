import logging

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.validators import RecipeUniqueValidator
from users.serializers import CustomUserSerializer


class ErrorMessage:
    EMPTY_INGREDIENTS_ERROR = 'Необходимо указать хотя бы один ингредиент'
    INGREDIENTS_REOCCURRENCE_ERROR = (
        'Одинаковые ингредиенты с одинаковой '
        'единицей измерения не должны повторяться'
    )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели ингредиентов в рецепте."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = Base64ImageField()
    tags = PresentablePrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        presentation_serializer=TagSerializer,
        read_source=None,
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def logger_warning(self, field):
        """Предупреждение об отсутствии ожидаемого аннотированного поля."""
        request = self.context['request']
        return (
            f'{request.path}: Запрос к базе данных не оптимален. '
            f'В {self.__class__.__name__} в переданном queryset '
            f'не аннотировано поле {field}'
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        field = 'is_favorited'
        if not hasattr(obj, field):
            logging.warning(self.logger_warning(field))
            return obj.followers.filter(user=request.user).exists()
        return obj.is_favorited

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        field = 'is_in_shopping_cart'
        if not hasattr(obj, field):
            logging.warning(self.logger_warning(field))
            return obj.carts.filter(user=request.user).exists()
        return obj.is_in_shopping_cart

    def validate(self, attrs):
        ingredients = attrs.get('recipe_ingredients', False)
        if not ingredients:
            raise serializers.ValidationError(
                ErrorMessage.EMPTY_INGREDIENTS_ERROR
            )
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(ingredient.get('ingredient').get('id'))
        if len(ingredient_list) > len(set(ingredient_list)):
            raise serializers.ValidationError(
                ErrorMessage.INGREDIENTS_REOCCURRENCE_ERROR
            )
        return attrs

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        recipe.author.is_subscribed = False
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', False)
        ingredients = validated_data.pop('recipe_ingredients', False)
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели избранных рецептов."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = (RecipeUniqueValidator(),)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели списка покупок."""
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = (RecipeUniqueValidator(),)
