import json
import os

from django.core.management.base import BaseCommand

from foodgram.settings import DATA_FILES_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loader to the database from a JSON file.'

    def handle(self, *args, **options):
        file_name = 'ingredients.json'
        json_path = os.path.join(DATA_FILES_DIR, file_name)
        try:
            with open(json_path, 'rb') as file:
                data = json.load(file)
                ingredients = [
                    Ingredient(
                        name=item.get('name'),
                        measurement_unit=item.get('measurement_unit'),
                    )
                    for item in data
                ]
                Ingredient.objects.bulk_create(ingredients)
            print('finished')
        except FileNotFoundError:

            print(f'File {file_name} not found.')
            return