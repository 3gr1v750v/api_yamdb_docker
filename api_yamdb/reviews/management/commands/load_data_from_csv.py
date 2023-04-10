import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

FIELDS = {
    'category': Category,
    'title': Title,
    'genre': Genre,
    'author': User,
    'review': Review,
}
CLASSES = [
    Category,
    Genre,
    Title,
    GenreTitle,
    User,
    Review,
    Comment,
]


def change_foreign_values(row_data):
    """Функция для замены значений id на связанные объекты в строке данных."""
    row_data_copy = row_data.copy()

    for field_key, field_value in zip(row_data.keys(), row_data.values()):
        if field_key in FIELDS.keys():
            row_data_copy[field_key] = FIELDS[field_key].objects.get(
                pk=field_value
            )
    return row_data_copy


def load_data():
    """
    Функция для загрузки данных из CSV, формирования пакета объектов
    для загрузки в базу и загрузки данных в базу.
    """
    for model_class in CLASSES:
        with open(
            settings.PATH_CSV_FILES[model_class.__qualname__.lower()],
            encoding='utf-8',
        ) as file:
            try:
                dr = csv.DictReader(
                    file,
                    delimiter=",",
                )
                to_db = []

                for row in dr:
                    row = change_foreign_values(row)
                    to_db.append(model_class(**row))

                model_class.objects.bulk_create(to_db)

            except (ValueError, IntegrityError) as error:
                print(
                    f'Ошибка в загружаемых данных. {error}. '
                    f'Данные в {model_class.__qualname__} не загружены.'
                )
                break
        print(f'Данные в {model_class.__qualname__} загружены.')


class Command(BaseCommand):
    """Класс для создания новой команды на добавление данных из csv файлов."""

    def handle(self, *args, **options):
        load_data()
