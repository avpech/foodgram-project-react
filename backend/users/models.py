from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Модель пользователей."""
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=150,
        help_text='Обязательное поле.'
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=150,
        help_text='Обязательное поле.',
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
        help_text='Обязательное поле.',
        db_index=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.CheckConstraint(
                check=~(
                    models.Q(username='me')
                    | models.Q(username='subscriptions')
                ),
                name='forbidden_usernames'
            ),
        )
        ordering = ('-date_joined',)


class Subscribe(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_authors',
        verbose_name='Пользователь',
        db_index=True,
        help_text='Обязательное поле.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
        db_index=True,
        help_text='Обязательное поле.'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='user_author_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_author_different'),
        )
        index_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-pk',)

    def __str__(self) -> str:
        return (
            f'Пописка: {self.user.get_username()} '
            f'на {self.author.get_username()}'
        )
