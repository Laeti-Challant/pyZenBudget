import calendar
from datetime import date as date_type, datetime

from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Transaction, Budget, Category, CategorizationRule

# En dessous de ce seuil, une catégorisation automatique est considérée peu fiable
# et remontée dans l'endpoint "review" même si une règle a matché.
LOW_CONFIDENCE_THRESHOLD = 0.2


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

    @action(detail=False, methods=["get"], url_path="review")
    def review(self, request):
        # Pas encore catégorisée, ou catégorisée automatiquement mais peu fiable.
        # NULL (pas de règle appliquée) est trié en premier par SQLite en ordre ascendant,
        # donc les non catégorisées passent avant les peu sûres.
        queryset = Transaction.objects.filter(
            Q(category__isnull=True) | Q(applied_rule__confidence__lt=LOW_CONFIDENCE_THRESHOLD),
            is_validated=False,
        ).order_by("applied_rule__confidence")

        transactions = [
            {
                "id": t.id,
                "date": t.date,
                "label": t.label,
                "amount": t.amount,
                "category_id": t.category_id,
                "category": t.category.name if t.category else "Uncategorized",
                "applied_rule": t.applied_rule.pattern if t.applied_rule else None,
                "confidence": t.applied_rule.confidence if t.applied_rule else None,
            }
            for t in queryset
        ]

        return Response({"transactions": transactions, "total": len(transactions)})

    @action(detail=False, methods=["get"], url_path="matches")
    def matches(self, request):
        pattern = request.query_params.get("pattern")

        if not pattern:
            return Response(
                {"error": "'pattern' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Transactions pas encore catégorisées dont le libellé contient le terme
        # (icontains = sous-chaîne, insensible à la casse).
        queryset = Transaction.objects.filter(
            category__isnull=True, label__icontains=pattern
        )

        transactions = [
            {
                "id": t.id,
                "date": t.date,
                "label": t.label,
                "amount": t.amount,
            }
            for t in queryset
        ]

        return Response({
            "pattern": pattern,
            "transactions": transactions,
            "total": len(transactions),
        })

    @action(detail=False, methods=["post"], url_path="categorize")
    def categorize(self, request):
        category_id = request.data.get("category_id")
        pattern = request.data.get("pattern")
        validated_ids = request.data.get("validated_ids", [])
        rejected_ids = request.data.get("rejected_ids", [])

        if not category_id or not pattern:
            return Response(
                {"error": "'category_id' and 'pattern' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {"error": f"Category '{category_id}' does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ne touche que les transactions encore non catégorisées (garde-fou).
        Transaction.objects.filter(
            id__in=validated_ids, category__isnull=True
        ).update(category=category, is_validated=True)

        rule, _ = CategorizationRule.objects.get_or_create(
            pattern=pattern, defaults={"category": category}
        )
        rule.usage_count += len(validated_ids)
        rule.rejected_count += len(rejected_ids)

        # Pas de recalcul tant qu'aucune validation ni rejet n'a eu lieu (division par zéro).
        total = rule.usage_count + rule.rejected_count
        if total > 0:
            rule.confidence = rule.usage_count / total

        rule.is_user_validated = True
        rule.save()

        return Response({
            "validated_count": len(validated_ids),
            "rejected_count": len(rejected_ids),
            "rule": {
                "pattern": rule.pattern,
                "category_id": rule.category_id,
                "confidence": rule.confidence,
                "usage_count": rule.usage_count,
                "rejected_count": rule.rejected_count,
            },
        })

    @action(detail=False, methods=["get"], url_path="yearly")
    def yearly(self, request):
        year_str = request.query_params.get("year")

        if not year_str:
            return Response(
                {"error": "'year' is required (format YYYY)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            year = int(year_str)
            if not (1900 <= year <= 9999):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": f"Invalid format for 'year': '{year_str}'. Use YYYY."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        first_day = date_type(year, 1, 1)
        last_day = date_type(year, 12, 31)

        # Dépensé par (mois, catégorie) en UNE seule requête (TruncMonth groupe par mois).
        spent_rows = (
            Transaction.objects.filter(
                date__range=[first_day, last_day], amount__lt=0
            )
            .annotate(month=TruncMonth("date"))
            .values("month", "category__id", "category__name")
            .annotate(spent=Sum("amount"))
            .order_by("month", "spent")
        )

        # Budgets de l'année : indexés par (mois, catégorie) pour le détail mensuel,
        # et sommés par catégorie pour le budget annuel (agrégat des mensuels).
        budget_by_month_cat = {}
        annual_budget_by_cat = {}
        cat_names = {}
        for b in Budget.objects.filter(period__year=year).select_related("category"):
            budget_by_month_cat[(b.period.month, b.category_id)] = b.amount
            annual_budget_by_cat[b.category_id] = (
                annual_budget_by_cat.get(b.category_id, 0) + b.amount
            )
            cat_names[b.category_id] = b.category.name

        # 12 mois toujours présents (pour le graphe), même vides.
        months = {m: [] for m in range(1, 13)}
        annual_spent_by_cat = {}

        # Assemblage des résultats déjà agrégés (pas un recalcul transaction par transaction).
        for row in spent_rows:
            m = row["month"].month
            cat_id = row["category__id"]
            spent = -row["spent"]  # exposé en positif
            months[m].append({
                "category_id": cat_id,
                "category": row["category__name"] or "Uncategorized",
                "spent": spent,
                "budget": budget_by_month_cat.get((m, cat_id)),
            })
            annual_spent_by_cat[cat_id] = annual_spent_by_cat.get(cat_id, 0) + spent
            cat_names.setdefault(cat_id, row["category__name"] or "Uncategorized")

        total_by_category = sorted(
            (
                {
                    "category_id": cat_id,
                    "category": cat_names.get(cat_id) or "Uncategorized",
                    "spent": spent,
                    "budget": annual_budget_by_cat.get(cat_id),
                }
                for cat_id, spent in annual_spent_by_cat.items()
            ),
            key=lambda item: item["spent"],
            reverse=True,  # plus grosse dépense annuelle en premier
        )

        return Response({
            "year": year,
            "total": {"by_category": total_by_category},
            "months": [
                {"month": f"{year}-{m:02d}", "by_category": months[m]}
                for m in range(1, 13)
            ],
        })
