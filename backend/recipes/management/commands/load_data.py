import csv
import os

import django.db.utils
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def read_csv(name_file):
    """Считывает данные из csv и возвращает список строк таблицы."""
    path = os.path.join('assets/data', name_file)
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        return list(reader)


class Command(BaseCommand):
    help = 'Импорт таблицы ingredients.csv в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--clear',
            action='store_true',
            help='Удаляет все данные из таблицы'
        )

    def handle(self, *args, **options):
        try:
            if options['clear']:
                Ingredient.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Таблица ингредиентов успешно очищена.'
                    )
                )
            else:
                table = read_csv('ingredients.csv')
                Ingredient.objects.bulk_create(
                    Ingredient(
                        name=row[0], measurement_unit=row[1]
                    ) for row in table
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        'Таблица ингредиентов загружена в базу данных.'
                    )
                )
        except django.db.utils.IntegrityError as e:
            self.stdout.write(
                self.style.ERROR('Ошибка загрузки. База данных не пуста. '
                                 'Совпадение уникальных полей. "%s"' % e))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Ошибка загрузки данных:'
                                               ' "%s"' % e))
