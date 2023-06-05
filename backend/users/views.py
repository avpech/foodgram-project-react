from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Subscribe
from users.serializers import SubscribeSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Управление пользователями."""
    http_method_names = ('get', 'head', 'options', 'post', 'delete')

    def permission_denied(self, request, **kwargs):
        """Отключение ненужных эндпоинтов Djoser."""
        if self.action in (
            'activation', 'resend_activation',
            'reset_password', 'reset_password_confirm',
            'set_username', 'reset_username',
            'reset_username_confirm',
        ):
            raise NotFound
        return super().permission_denied(request, **kwargs)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset()
        return super().get_queryset().annotate(
            is_subscribed=Exists(Subscribe.objects.filter(
                user=self.request.user,
                author=OuterRef('pk')
            ))
        )

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Просмотр своей учетной записи."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    def get_subscriptions(self):
        return (
            Subscribe.objects
            .filter(user=self.request.user)
            .annotate(
                is_subscribed=Value(True),
                recipes_count=Count('author__recipes')
            )
            .select_related('author')
            .prefetch_related('author__recipes')
            .order_by('-pk')
        )

    @action(
        ('get',), detail=False,
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        """Просмотр подписок пользователя."""
        self.get_queryset = self.get_subscriptions
        return self.list(request, *args, **kwargs)

    @action(
        ('post',), detail=True,
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Создание подписки."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        author = get_object_or_404(User, id=id)
        serializer.save(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Удаление подписки."""
        subscribtion = get_object_or_404(
            Subscribe, user=request.user, author=id
        )
        subscribtion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
