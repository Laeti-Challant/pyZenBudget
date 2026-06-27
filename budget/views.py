from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Transaction


class TransactionViewSet(ViewSet):

    @action(detail=False, methods=["get"], url_path="synthese")
    def synthese(self, request):
        debut = request.query_params.get("debut")
        fin = request.query_params.get("fin")

        if not debut or not fin:
            return Response(
                {"erreur": "Les paramètres 'debut' et 'fin' sont obligatoires (format YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Transaction.objects.filter(date__range=[debut, fin])

        totaux = qs.aggregate(
            total_depenses=Sum("amount", filter=Q(amount__lt=0)),
            total_revenus=Sum("amount", filter=Q(amount__gt=0)),
        )

        total_depenses = totaux["total_depenses"] or 0
        total_revenus = totaux["total_revenus"] or 0

        par_categorie = (
            qs.values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("total")
        )

        return Response({
            "periode": {"debut": debut, "fin": fin},
            "total_depenses": total_depenses,
            "total_revenus": total_revenus,
            "solde": total_revenus + total_depenses,
            "par_categorie": [
                {
                    "categorie": item["category__name"] or "Non catégorisé",
                    "total": item["total"],
                }
                for item in par_categorie
            ],
        })
