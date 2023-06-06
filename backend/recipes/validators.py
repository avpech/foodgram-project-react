from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError


class RecipeUniqueValidator:
    """Невозможность повторного добавления рецепта в избранное/корзину."""
    requires_context = True

    def __call__(self, attrs, serializer):
        user = serializer.context['request'].user
        recipe_id = int(serializer.context['view'].kwargs.get('pk'))
        if serializer.Meta.model.objects.filter(
            user=user, recipe=recipe_id
        ).exists():
            raise ValidationError(
                (f'Рецепт уже добавлен в '
                 f'{serializer.Meta.model._meta.verbose_name}.')
            )
        return attrs


class ColorHexCodeValidator(RegexValidator):
    """Валидация на корректный цветовой HEX-код."""
    regex = r'^#([0-9a-fA-F]{2}){3}$'
    message = 'Введите корректный цветовой HEX-код. Пример: #49B64E'
