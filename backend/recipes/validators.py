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
                ('Рецепт уже добавлен в {}.'
                 .format(serializer.Meta.model._meta.verbose_name))
            )
        return attrs
