from datetime import date as date_type

from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Transaction


def _validate_dates(start_str, end_str):
    """Validates and converts two YYYY-MM-DD strings. Raises ValueError if invalid."""
    try:
        start = date_type.fromisoformat(start_str)
    except ValueError:
        raise ValueError(f"Invalid format for 'start': '{start_str}'. Use YYYY-MM-DD.")
    try:
        end = date_type.fromisoformat(end_str)
    except ValueError:
        raise ValueError(f"Invalid format for 'end': '{end_str}'. Use YYYY-MM-DD.")
    if end < start:
        raise ValueError("'end' cannot be earlier than 'start'.")
    return start, end


class TransactionViewSet(ViewSet):

    def list(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        category_id = request.query_params.get("category")

        queryset = Transaction.objects.select_related("category").order_by("-date")

        if start or end:
            if not (start and end):
                return Response(
                    {"error": "'start' and 'end' must be provided together (format YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                start_date, end_date = _validate_dates(start, end)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(date__range=[start_date, end_date])

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        transactions = [
            {
                "id": t.id,
                "date": t.date,
                "label": t.label,
                "amount": t.amount,
                "category_id": t.category_id,
                "category": t.category.name if t.category else "Uncategorized",
            }
            for t in queryset
        ]

        return Response({"transactions": transactions, "total": len(transactions)})

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if not start or not end:
            return Response(
                {"error": "'start' and 'end' are required (format YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date, end_date = _validate_dates(start, end)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Transaction.objects.filter(date__range=[start_date, end_date])

        totals = queryset.aggregate(
            total_expenses=Sum("amount", filter=Q(amount__lt=0)),
            total_income=Sum("amount", filter=Q(amount__gt=0)),
        )

        total_expenses = totals["total_expenses"] or 0
        total_income = totals["total_income"] or 0

        by_category = (
            queryset.values("category__id", "category__name")
            .annotate(total=Sum("amount"))
            .order_by("total")
        )

        return Response({
            "period": {"start": start_date, "end": end_date},
            "total_expenses": total_expenses,
            "total_income": total_income,
            "balance": total_income + total_expenses,
            "by_category": [
                {
                    "category_id": item["category__id"],
                    "category": item["category__name"] or "Uncategorized",
                    "total": item["total"],
                }
                for item in by_category
            ],
        })
