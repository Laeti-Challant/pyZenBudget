from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Catégorie de dépense ou revenu."""

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nom de la catégorie"
    )

    # Pour créer des hiérarchies (ex: Alimentation > Restaurants)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name="Catégorie parente",
    )

    # Couleur pour les graphiques (format hex: #FF5733)
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Couleur")

    # Type : dépense ou revenu
    TRANSACTION_TYPES = [
        ("expense", "Dépense"),
        ("income", "Revenu"),
    ]
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES, default="expense", verbose_name="Type"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Transaction bancaire importée."""

    date = models.DateField(verbose_name="Date")

    label = models.TextField(verbose_name="Libellé")

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant"
    )

    # Catégorie assignée (peut être vide au départ)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="Catégorie",
    )

    # L'utilisateur a-t-il validé cette catégorisation ?
    is_validated = models.BooleanField(default=False, verbose_name="Validée")

    # Pour détecter les doublons
    import_hash = models.CharField(
        max_length=32, unique=True, verbose_name="Hash d'import"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-date"]  # Les plus récentes en premier
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.date} - {self.label[:50]} - {self.amount}€"


class CategorizationRule(models.Model):
    """Règle pour catégoriser automatiquement les transactions."""

    # Pattern à rechercher dans le libellé (ex: "SNCF", "CARREFOUR")
    pattern = models.CharField(max_length=200, unique=True, verbose_name="Motif")

    # Catégorie à appliquer si le pattern match
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name="Catégorie",
    )

    # Score de confiance (0.0 à 1.0)
    confidence = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Confiance",
    )

    # La règle vient d'une validation utilisateur ?
    is_user_validated = models.BooleanField(
        default=False, verbose_name="Validée par l'utilisateur"
    )

    # Nombre de fois où la règle a été utilisée
    usage_count = models.IntegerField(default=0, verbose_name="Nombre d'utilisations")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Règle de catégorisation"
        verbose_name_plural = "Règles de catégorisation"
        ordering = ["-confidence", "-usage_count"]

    def __str__(self):
        return f"{self.pattern} → {self.category.name} ({self.confidence})"


class Budget(models.Model):
    """Plafond de dépenses mensuel par catégorie.

    `period` contient toujours le 1er du mois (ex: 2026-06-01 pour juin 2026).
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="budgets",
        verbose_name="Catégorie",
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Plafond mensuel"
    )

    period = models.DateField(verbose_name="Mois (1er du mois)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        unique_together = [["category", "period"]]
        ordering = ["-period"]

    def __str__(self):
        return f"{self.category.name} : {self.amount}€ ({self.period.strftime('%B %Y')})"
