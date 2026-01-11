import pandas as pd
from pathlib import Path
from datetime import datetime


class ExcelNormalizer:
    """
    Normalise un fichier Excel bancaire vers un format standard.
    """

    def __init__(self, raw_file_path: str, start_row: int = 9):
        """
        Args:
            raw_file_path: Chemin vers le fichier brut
            start_row: Ligne de début des données (0-indexed, donc 9 = ligne 10 Excel)
        """
        self.raw_file_path = Path(raw_file_path)
        self.start_row = start_row
        self.df = None

    def read_file(self) -> pd.DataFrame:
        """Lit le fichier Excel en sautant les lignes d'en-tête."""
        try:
            # skiprows=9 saute les 10 premières lignes (0 à 9)
            self.df = pd.read_excel(self.raw_file_path, skiprows=self.start_row)
            print(f"✓ Fichier lu : {len(self.df)} lignes")
            print(f"✓ Colonnes : {list(self.df.columns)}")
            return self.df
        except Exception as e:
            print(f"✗ Erreur lecture fichier : {e}")
            raise

    def normalize(self) -> pd.DataFrame:
        """
        Normalise le DataFrame vers le format standard.

        Transformations :
        - Date → format ISO (YYYY-MM-DD)
        - Crédit - Débit → Amount (signé)
        - Renomme les colonnes
        """
        if self.df is None:
            raise ValueError("Aucun fichier chargé. Appelez read_file() d'abord.")

        # Crée une copie pour ne pas modifier l'original
        df_normalized = self.df.copy()

        # 1. Normalise la date
        df_normalized["Date"] = pd.to_datetime(
            df_normalized["Date"],  # ← Adapte le nom de ta colonne
            dayfirst=True,  # Format français DD/MM/YYYY
        ).dt.strftime("%Y-%m-%d")

        # 2. Calcule le montant : Crédit - Débit
        # Les débits sont souvent positifs dans les fichiers bancaires
        # On les convertit en négatifs
        debit = df_normalized["Débit euros"].fillna(0)  # ← Adapte le nom
        credit = df_normalized["Crédit euros"].fillna(0)  # ← Adapte le nom

        df_normalized["Amount"] = credit - debit

        # 3. Renomme le libellé
        df_normalized["Label"] = df_normalized["Libellé"]  # ← Adapte le nom

        # 4. Garde seulement les colonnes nécessaires
        df_normalized = df_normalized[["Date", "Label", "Amount"]]

        # 5. Supprime les lignes vides
        df_normalized = df_normalized.dropna(subset=["Label"])

        # 6. Trie par date
        df_normalized = df_normalized.sort_values("Date")

        print(f"✓ {len(df_normalized)} transactions normalisées")

        return df_normalized

    def save_normalized(self, output_dir: str = "data/processed") -> Path:
        """
        Sauvegarde le fichier normalisé.

        Returns:
            Path vers le fichier sauvegardé
        """
        if self.df is None:
            raise ValueError("Aucune donnée à sauvegarder")

        # Crée le dossier s'il n'existe pas
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Nom du fichier : ajoute _normalized + timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = (
            output_path / f"{self.raw_file_path.stem}_normalized_{timestamp}.xlsx"
        )

        # Normalise et sauvegarde
        df_normalized = self.normalize()
        df_normalized.to_excel(output_file, index=False)

        print(f"✓ Fichier sauvegardé : {output_file}")

        return output_file
