from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

from recipes.validators import ColorHexCodeValidator

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=50,
        verbose_name='Название тега',
        unique=True,
        help_text='Обязательное поле'
    )
    color = models.CharField(
        max_length=7,
        validators=(ColorHexCodeValidator(),),
        verbose_name='Цветовой HEX-код',
        help_text='Обязательное поле. Пример: #49B64E'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг тега',
        unique=True,
        db_index=True,
        help_text='Обязательное поле'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента',
        db_index=True,
        help_text='Обязательное поле'
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='Единица измерения',
        help_text='Обязательное поле'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_measurement_unique'
            ),
        )
        index_together = ('name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class RecipeQuerySet(models.QuerySet):
    """QuerySet для модели Recipe."""

    def add_is_favorited(self, user):
        return self.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )),
        )

    def add_is_in_shopping_cart(self, user):
        return self.annotate(
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )),
        )


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        db_index=True,
        help_text='Обязательное поле'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        db_index=True,
        help_text='Обязательное поле'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта',
        help_text='Обязательное поле.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
        help_text='Обязательное поле'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Обязательное поле'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(settings.MIN_COOKING_TIME),),
        verbose_name='Время приготовления',
        help_text='Обязательное поле'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        # прим. Не стал (не смог) менять на ingredients, поскольку в модели
        # Recipe явно указано many-to-many поле ingredients, и конфликт
        # имен вызывает у Джанго глубокое возмущение )
        # А отказываться от явного указания поля не хочется, потому что
        # благодаря ему можно использовать метод clear()
        verbose_name='Рецепт',
        db_index=True,
        help_text='Обязательное поле'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipes_with_ingredient',
        # тут аналогично - в вышеупомянутом поле ingredients
        # уже указано related_name recipes.
        verbose_name='Ингредиент',
        db_index=True,
        help_text='Обязательное поле'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(settings.MIN_INGREDIENT_AMOUNT),),
        verbose_name='Количество',
        help_text='Обязательное поле'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_unique'
            ),
        )
        index_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self) -> str:
        return (
            f'Ингредиент: {self.ingredient.name}; '
            f'рецепт: {self.recipe.name}'
        )


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
        db_index=True,
        help_text='Обязательное поле'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Рецепт',
        db_index=True,
        help_text='Обязательное поле'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorite_unique'
            ),
        )
        index_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-pk',)

    def __str__(self) -> str:
        return (
            f'Избранный рецепт "{self.recipe}" '
            f'пользователя {self.user}'
        )


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        db_index=True,
        help_text='Обязательное поле'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт',
        db_index=True,
        help_text='Обязательное поле'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_unique'
            ),
        )
        index_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-pk',)

    def __str__(self) -> str:
        return (
            f'Рецепт "{self.recipe}" в списке покупок '
            f'пользователя {self.user}'
        )
