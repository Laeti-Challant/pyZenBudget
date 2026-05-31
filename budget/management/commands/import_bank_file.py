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
            default=10,
            help="Ligne de début des données (défaut: 10)",
        )
        parser.add_argument(
            "--date-column",
            type=str,
            default= "Date",
            help="Intitulé de la colonne comportant les dates"
        )
        parser.add_argument(
            "--debit-column",
            type=str,
            default= "Débit euros",
            help="Intitulé de la colonne comportant les dépenses"
        )
        parser.add_argument(
            "--credit-column",
            type=str,
            default= "Crédit euros",
            help="Intitulé de la colonne comportant les crédits"
        )
        parser.add_argument(
            "--label-column",
            type=str,
            default= "Libellé",
            help="Intitulé de la colonne comportant les libellés"
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        start_row = options["start_row"]
        date_column = options["date_column"]
        debit_column = options["debit_column"]
        credit_column = options["credit_column"]
        label_column = options["label_column"]

        # Vérifie que le fichier existe
        if not Path(file_path).exists():
            raise CommandError(f"Fichier non trouvé : {file_path}")

        self.stdout.write(self.style.SUCCESS(f"\n📂 Import de : {file_path}\n"))

        # Étape 1 : Normalisation
        self.stdout.write("🔄 Normalisation...")
        normalizer = ExcelNormalizer(file_path, start_row=start_row, date_column=date_column, debit_column=debit_column, credit_column=credit_column, label_column=label_column)
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
