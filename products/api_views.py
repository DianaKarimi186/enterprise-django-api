from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializers import CategorySerializer


class CategoryListView(ListAPIView):
    """Return categories available when creating inventory items."""

    queryset = Category.objects.order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class DashboardMetricsView(APIView):
    """Return inventory metrics for the authenticated user's products."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(owner=request.user)
        totals = products.aggregate(
            total_products=Count("id"),
            total_stock=Sum("stock"),
            low_stock_count=Count("id", filter=__import__("django.db.models", fromlist=["Q"]).Q(stock__gt=0, stock__lte=5)),
            out_of_stock_count=Count("id", filter=__import__("django.db.models", fromlist=["Q"]).Q(stock=0)),
            total_inventory_value=Sum(
                ExpressionWrapper(
                    F("price") * F("stock"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            ),
        )
        return Response({
            "total_products": totals["total_products"] or 0,
            "total_stock": totals["total_stock"] or 0,
            "low_stock_count": totals["low_stock_count"] or 0,
            "out_of_stock_count": totals["out_of_stock_count"] or 0,
            "category_count": products.values("category_id").distinct().count(),
            "total_inventory_value": str(totals["total_inventory_value"] or 0),
        })
