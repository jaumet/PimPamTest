import json

from django.core.management.base import BaseCommand

from exercises.importer import import_exercises


class Command(BaseCommand):
    help = "Importa exercicis des d'un fitxer JSON amb una array d'exercicis."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"], encoding="utf-8") as handle:
            payload = json.load(handle)
        created = import_exercises(payload)
        self.stdout.write(self.style.SUCCESS(f"S'han importat {len(created)} exercicis."))
