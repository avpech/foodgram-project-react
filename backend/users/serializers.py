import logging

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для просмотра пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        if not hasattr(obj, 'is_subscribed'):
            logging.warning(
                f'{request.path}: Запрос к базе данных не оптимален. '
                f'В {self.__class__.__name__} в переданном queryset '
                'не аннотировано поле is_subscribed'
            )
            return obj.subscribers.filter(user=request.user).exists()
        return obj.is_subscribed


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )


class BrieflyRecipeSerializer(serializers.ModelSerializer):
    """Краткое отображение рецепта."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для управления подписками."""
    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username',
                                     read_only=True)
    first_name = serializers.CharField(source='author.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='author.last_name',
                                      read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    class ErrorMessage:
        SUBSCRIPTION_EXISTS_ERROR = 'Подписка уже существует.'
        SELF_FOLLOWING_ERROR = 'Пользователь не может подписаться на себя.'

    def logger_warning(self, field):
        """Предупреждение об отсутствии ожидаемого аннотированного поля."""
        request = self.context['request']
        return (
            f'{request.path}: Запрос к базе данных не оптимален. '
            f'В {self.__class__.__name__} в переданном queryset '
            f'не аннотировано поле {field}'
        )

    def get_recipes(self, obj):
        request = self.context['request']
        try:
            recipes_limit = int(request.query_params.get('recipes_limit'))
        except Exception:
            recipes_limit = None
        queryset = obj.author.recipes.all()
        if recipes_limit is not None and recipes_limit > 0:
            queryset = queryset[:recipes_limit]
        return BrieflyRecipeSerializer(
            queryset, many=True, context=self.context
        ).data

    def get_is_subscribed(self, obj):
        request = self.context['request']
        field = 'is_subscribed'
        if not hasattr(obj, field):
            logging.warning(self.logger_warning(field))
            return obj.user == request.user
        return obj.is_subscribed

    def get_recipes_count(self, obj):
        field = 'recipes_count'
        if not hasattr(obj, field):
            logging.warning(self.logger_warning(field))
            return obj.author.recipes.count()
        return obj.recipes_count

    def validate(self, attrs):
        user = self.context['request'].user
        author_id = int(self.context['view'].kwargs.get('id'))
        if Subscribe.objects.filter(user=user, author=author_id).exists():
            raise serializers.ValidationError(
                self.ErrorMessage.SUBSCRIPTION_EXISTS_ERROR
            )
        if author_id == user.id:
            raise serializers.ValidationError(
                self.ErrorMessage.SELF_FOLLOWING_ERROR
            )
        return attrs

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.is_subscribed = True
        return obj
