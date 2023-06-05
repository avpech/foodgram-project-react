from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from recipes import models
from users.models import Subscribe

User = get_user_model()


GROUPS_PERMISSIONS = {
    'Admin': {
        models.User: ['add', 'change', 'delete', 'view'],
        models.Recipe: ['change', 'delete', 'view'],
        models.Ingredient: ['add', 'change', 'delete', 'view'],
        models.RecipeIngredient: ['add', 'change', 'delete', 'view'],
        models.Tag: ['add', 'change', 'delete', 'view'],
        models.Favorite: ['view'],
        models.ShoppingCart: ['view'],
        Subscribe: ['view'],
    },
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = 'Создание групп пользователей'

    def handle(self, *args, **options):
        for group_name in GROUPS_PERMISSIONS:
            group, created = Group.objects.get_or_create(name=group_name)
            for model_cls in GROUPS_PERMISSIONS[group_name]:
                for perm_name in GROUPS_PERMISSIONS[group_name][model_cls]:
                    codename = perm_name + '_' + model_cls._meta.model_name
                    try:
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write('Adding '
                                          + codename
                                          + ' to group '
                                          + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + ' not found')
