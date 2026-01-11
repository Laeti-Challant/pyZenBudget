from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from budget.importers.excel_normalizer import ExcelNormalizer
from budget.importers.excel_importer import TransactionImporter


class Command(BaseCommand):
    help = "Importe un fichier bancaire (Excel ou CSV)"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="Chemin vers le fichier à importer"
        )
        parser.add_argument(
            "--start-row",
            type=int,
            default=9,
            help="Ligne de début des données (défaut: 9)",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        start_row = options["start_row"]

        # Vérifie que le fichier existe
        if not Path(file_path).exists():
            raise CommandError(f"Fichier non trouvé : {file_path}")

        self.stdout.write(self.style.SUCCESS(f"\n📂 Import de : {file_path}\n"))

        # Étape 1 : Normalisation
        self.stdout.write("🔄 Normalisation...")
        normalizer = ExcelNormalizer(file_path, start_row=start_row)
        normalizer.read_file()
        normalized_file = normalizer.save_normalized()

        # Étape 2 : Import en BDD
        self.stdout.write("💾 Import en base de données...")
        importer = TransactionImporter(normalized_file)
        importer.read_file()
        created, duplicates = importer.import_to_db()

        # Résumé
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Import terminé !\n"
                f"   Nouvelles : {created}\n"
                f"   Doublons : {duplicates}\n"
            )
        )
