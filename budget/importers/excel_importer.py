import pandas as pd
import hashlib
from pathlib import Path
from typing import List, Dict


class TransactionImporter:
    """
    Importe des transactions depuis un fichier Excel NORMALISÉ.
    Attend les colonnes : Date, Label, Amount
    """

    def __init__(self, normalized_file_path: str):
        self.file_path = Path(normalized_file_path)
        self.df = None

    def read_file(self) -> pd.DataFrame:
        # Lit le fichier normalisé.
        try:
            self.df = pd.read_excel(self.file_path)

            # Vérifie que les colonnes requises existent
            required_columns = ["Date", "Label", "Amount"]
            missing = [col for col in required_columns if col not in self.df.columns]

            if missing:
                raise ValueError(f"Colonnes manquantes : {missing}")

            print(f"✓ Fichier normalisé lu : {len(self.df)} lignes")
            return self.df

        except Exception as e:
            print(f"✗ Erreur lecture fichier : {e}")
            raise

    def prepare_transactions(self) -> List[Dict]:
        """
        Prépare les transactions pour l'import en BDD.

        Returns:
            Liste de dictionnaires prêts pour Django
        """
        if self.df is None:
            raise ValueError("Aucun fichier chargé")

        transactions = []

        occurence_cache = {}

        for index, row in self.df.iterrows():
            try:
                date_str = str(row["Date"])
                label = str(row["Label"])
                amount = float(row["Amount"])

                # Parse la date
                date = pd.to_datetime(date_str).date()

                # création de la chaine de base (pour vérification des occurences)
                base_string = f"{date}{label}{amount}"

                if base_string in occurence_cache:
                    occurence_cache[base_string] += 1
                    occurence_count = occurence_cache[base_string]
                    hash_string = f"{base_string}_{occurence_count}"
                else:
                    occurence_cache[base_string] = 0
                    hash_string = base_string

                # Crée un hash unique

                import_hash = hashlib.md5(hash_string.encode()).hexdigest()

                transactions.append(
                    {
                        "date": date,
                        "label": label,
                        "amount": amount,
                        "import_hash": import_hash,
                    }
                )

            except Exception as e:
                print(f"⚠ Ligne {index} ignorée : {e}")
                continue

        print(f"✓ {len(transactions)} transactions préparées")
        return transactions

    def import_to_db(self) -> tuple:
        """
        Sauvegarde les transactions en base de données.

        Returns:
            (nombre créées, nombre doublons)
        """
        from budget.models import Transaction

        transactions = self.prepare_transactions()

        created_count = 0
        duplicate_count = 0

        for trans_data in transactions:
            try:
                transaction, created = Transaction.objects.get_or_create(
                    import_hash=trans_data["import_hash"], defaults=trans_data
                )

                if created:
                    created_count += 1
                else:
                    duplicate_count += 1

            except Exception as e:
                print(f"✗ Erreur sauvegarde : {e}")
                continue

        print(f"✓ {created_count} nouvelles transactions")
        print(f"○ {duplicate_count} doublons ignorés")

        return created_count, duplicate_count
