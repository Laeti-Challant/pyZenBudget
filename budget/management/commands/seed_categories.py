from django.core.management.base import BaseCommand
from budget.models import Category


class Command(BaseCommand):
    help = "Crée les catégories de base"

    def handle(self, *args, **kwargs):
        categories = [
            {"name": "Alimentation", "transaction_type": "expense", "color": "#10B981"},
            {"name": "Transport", "transaction_type": "expense", "color": "#3B82F6"},
            {"name": "Logement", "transaction_type": "expense", "color": "#F59E0B"},
            {"name": "Loisirs", "transaction_type": "expense", "color": "#EC4899"},
            {"name": "Santé", "transaction_type": "expense", "color": "#EF4444"},
            {"name": "Salaire", "transaction_type": "income", "color": "#22C55E"},
            {"name": "Autre", "transaction_type": "expense", "color": "#6B7280"},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(**cat_data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Catégorie créée : {category.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"○ Catégorie existe déjà : {category.name}")
                )
