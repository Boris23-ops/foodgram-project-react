"""
Команда для импота ингридиентов в БД.
"""
import json
from tqdm import tqdm

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда импорта ингридиентов в базу данных."""
    help = 'Импорт ингридиентов из файла json'

    BASE_DIR = settings.BASE_DIR

    def handle(self, *args, **options):
        try:
            path = self.BASE_DIR / 'data/ingredients.json'
            with open(path, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)
                total_items = len(data)
                with tqdm(
                    total=total_items,
                    desc='Импорт ингредиентов',
                    unit='шт'
                ) as pbar:
                    for item in data:
                        Ingredient.objects.get_or_create(**item)
                        pbar.update(1)
        except CommandError as error:
            raise CommandError from error
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены'))
