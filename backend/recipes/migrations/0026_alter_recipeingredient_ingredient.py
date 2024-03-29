# Generated by Django 3.2 on 2023-06-06 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0025_auto_20230606_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(help_text='Обязательное поле', on_delete=django.db.models.deletion.PROTECT, related_name='recipes_with_ingredient', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
    ]
