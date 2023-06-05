from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.forms import CustomUserCreationForm
from users.models import Subscribe, User


class SubscribeInLine(admin.TabularInline):
    model = Subscribe
    fk_name = 'user'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = (
        'date_joined',
        'last_login',
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    add_form = CustomUserCreationForm
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active',
                   'groups', 'username', 'email')
    empty_value_display = '-пусто-'
    inlines = (SubscribeInLine,)

    def get_fieldsets(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {
                    'fields': ('first_name', 'last_name', 'email')
                }),
                (_('Permissions'), {
                    'fields': ('is_active', 'is_staff',
                               'is_superuser', 'groups'),
                }),
                (_('Important dates'), {
                    'fields': ('last_login', 'date_joined')
                }),
            )
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()
        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
            }
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
            }
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form

    def has_change_permission(self, request, obj=None):
        if (
            not request.user.is_superuser
            and obj is not None
            and obj.is_superuser
        ):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if (
            not request.user.is_superuser
            and obj is not None
            and obj.is_superuser
        ):
            return False
        return super().has_change_permission(request, obj)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    search_fields = ('user', 'author')
