![yamdb workflow](https://github.com/avpech/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
#### Проект "Продуктовый помощник".

### Описание
Проект "Продуктовый помощник - онлайн сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Стек технологий использованный в проекте:
- Python 3.7
- Django 3.2
- DRF
- Djoser
- Gunicorn
- Nginx
- Docker

### Запуск проекта
- Клонировать репозиторий и перейти в него в командной строке.
- Создать в каталоге infra_local файл .env в соответствии со следующим шаблоном:

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=some_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=django_secret_key
```
- Перейти в каталог infra_local.
- Собрать контейнеры (в ОС должен быть установлен Docker)

```bash
docker-compose up -d
```
Внимание: при работе в ОС Windows убедитесь, что в файле backend/start.sh для окончания строки используется LF, а не CRLF.

- Создать суперпользователя

```bash
docker-compose exec backend python manage.py createsuperuser
```

- Заполнить базу ингредиентами командой:

```bash
docker-compose exec backend python manage.py load_data
```

- Добавить желаемые теги рецептов в админке [localhost/admin](http://localhost/admin)

- Если есть необходимость, очистить базу от данных можно командой:

```bash
docker-compose exec backend python manage.py load_data -с
```

- Если есть необходимость, создаем для админ-зоны группу администраторов  командой:

```bash
docker-compose exec backend python manage.py add_admin_group
```

Проект запущен и доступен по адресу: [localhost](http://localhost)
Документация к API доступна по адресу: [localhost/api/docs/redoc.html](http://localhost/api/docs/redoc.html)

##### Об авторе
Артур Печенюк
- :white_check_mark: [avpech](https://github.com/avpech)
