# Generated by Django 3.2 on 2023-05-26 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230526_1812'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ('-pk',), 'verbose_name': 'Рецепт в списке покупок', 'verbose_name_plural': 'Список покупок'},
        ),
    ]
