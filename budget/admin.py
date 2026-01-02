from django.contrib import admin
from .models import Category, Transaction, CategorizationRule


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "transaction_type", "parent", "color"]
    list_filter = ["transaction_type"]
    search_fields = ["name"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "label", "amount", "category", "is_validated"]
    list_filter = ["is_validated", "category", "date"]
    search_fields = ["label"]
    date_hierarchy = "date"


@admin.register(CategorizationRule)
class CategorizationRuleAdmin(admin.ModelAdmin):
    list_display = [
        "pattern",
        "category",
        "confidence",
        "usage_count",
        "is_user_validated",
    ]
    list_filter = ["is_user_validated", "category"]
    search_fields = ["pattern"]
