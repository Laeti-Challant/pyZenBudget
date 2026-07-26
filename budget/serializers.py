from rest_framework import serializers

from .models import Category, Transaction, CategorizationRule


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent", "color", "transaction_type"]


class TransactionSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), allow_null=True, required=False
    )
    category = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "date",
            "label",
            "amount",
            "category_id",
            "category",
            "is_validated",
            "applied_rule",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        return obj.category.name if obj.category else "Uncategorized"


class CategorizationRuleSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all()
    )
    category = serializers.SerializerMethodField()

    class Meta:
        model = CategorizationRule
        fields = [
            "id",
            "pattern",
            "category_id",
            "category",
            "confidence",
            "is_user_validated",
            "usage_count",
            "rejected_count",
            "created_at",
        ]

    def get_category(self, obj):
        return obj.category.name
