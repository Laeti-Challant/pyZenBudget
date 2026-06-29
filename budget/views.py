import calendar
from datetime import date as date_type, datetime

from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Transaction, Budget


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


def _parse_month(month_str):
    """Parses 'YYYY-MM' into (first_day, last_day) of that month. Raises ValueError if invalid."""
    try:
        first_day = datetime.strptime(month_str, "%Y-%m").date()
    except (ValueError, TypeError):
        raise ValueError(f"Invalid format for 'month': '{month_str}'. Use YYYY-MM.")
    last_day = first_day.replace(
        day=calendar.monthrange(first_day.year, first_day.month)[1]
    )
    return first_day, last_day


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

    @action(detail=False, methods=["get"], url_path="monthly")
    def monthly(self, request):
        month = request.query_params.get("month")

        if not month:
            return Response(
                {"error": "'month' is required (format YYYY-MM)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            first_day, last_day = _parse_month(month)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Dépensé par catégorie sur le mois (les sommes sont calculées par l'ORM).
        # amount < 0 : on ne garde que les dépenses, pas les revenus.
        spent_by_category = (
            Transaction.objects.filter(
                date__range=[first_day, last_day], amount__lt=0
            )
            .values("category__id", "category__name")
            .annotate(spent=Sum("amount"))
            .order_by("spent")  # plus grosse dépense en premier (sommes négatives)
        )

        # Budgets du mois, indexés par catégorie pour une fusion en O(1).
        budgets = {
            b.category_id: b.amount
            for b in Budget.objects.filter(period=first_day)
        }

        # Assemblage de deux résultats déjà agrégés (ce n'est pas un calcul en Python).
        by_category = [
            {
                "category_id": item["category__id"],
                "category": item["category__name"] or "Uncategorized",
                "spent": -item["spent"],  # exposé en positif
                "budget": budgets.get(item["category__id"]),
            }
            for item in spent_by_category
        ]

        return Response({
            "month": first_day.strftime("%Y-%m"),
            "by_category": by_category,
        })
