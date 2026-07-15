from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job
from decimal import Decimal, InvalidOperation
from django.core.cache import cache
INVENTORY_CACHE_KEY = "inventory_products"

# --- Month 1 Rest API Views (For Mobile/Third-Party Clients) ---
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        simulate_heavy_background_job.delay(instance.name)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer


class DashboardView(View):
    def get(self, request):
        products = cache.get(INVENTORY_CACHE_KEY)

        if products is None:
            print("CACHE MISS → Querying database")

            products = list(
                Product.objects
                .select_related("category")
                .all()
            )

            cache.set(
                INVENTORY_CACHE_KEY,
                products,
                timeout=300
            )

        else:
            print("CACHE HIT → Using Redis")

        return render(
            request,
            "products/dashboard.html",
            {"products": products}
        )


class HTMXCreateProductView(View):
    def post(self, request):
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description', '')

        if not name:
            return render(
                request,
                'products/partials/form_errors.html',
                {'error_message': 'Product name is required.'},
                status=422
            )

        try:
            price = Decimal(price)

            if price <= 0:
                raise ValueError

        except (InvalidOperation, TypeError, ValueError):
            return render(
                request,
                'products/partials/form_errors.html',
                {'error_message': 'Price must be greater than zero.'},
                status=422
            )

        try:
            stock = int(stock)

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):
            return render(
                request,
                'products/partials/form_errors.html',
                {'error_message': 'Stock cannot be negative.'},
                status=422
            )

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description
        )
  

        simulate_heavy_background_job.delay(product.name)

        return render(
            request,
            'products/partials/products_row.html',
            {'product': product}
        )

class DeleteProductView(View):
    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if product:
            product.delete()

 
        if not Product.objects.exists():
            return render(
                request,
                "products/partials/empty_table.html"
            )

        return HttpResponse("")
    

class HTMXEditProductView(View):
    """Returns the inline edit form for a single product."""

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)

        return render(
            request,
            'products/partials/product_edit_row.html',
            {'product': product}
        )

class HTMXUpdateProductView(View):
    """Updates a product and returns the refreshed table row."""

    def put(self, request, pk):
        from django.http import QueryDict

        product = Product.objects.get(pk=pk)

        data = QueryDict(request.body)

        name = data.get('name')
        price = data.get('price')
        stock = data.get('stock')

        if not name or price in (None, '') or stock in (None, ''):
            return HttpResponse(
                "Missing required fields.",
                status=400
            )

        product.name = name
        product.price = price
        product.stock = stock
        product.save()

           

        return render(
            request,
            'products/partials/products_row.html',
            {'product': product}
        )