from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms.fields import EmailField

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания нового пользователя в админке."""

    class Meta:
        model = User
        fields = ('username', 'email')
        field_classes = {'username': UsernameField, 'email': EmailField}
