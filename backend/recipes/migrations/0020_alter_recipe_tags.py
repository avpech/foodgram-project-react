# Generated by Django 3.2 on 2023-06-04 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Обязательное поле', related_name='recipes', to='recipes.Tag', verbose_name='Теги рецепта'),
        ),
    ]
