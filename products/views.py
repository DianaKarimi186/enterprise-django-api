from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job

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


# --- Month 2 HTMX Frontend Views (For Browser Controls) ---
class DashboardView(View):
    """Renders the main visual interface panel showing all database objects"""
    def get(self, request):
        products = Product.objects.select_related('category').all()
        return render(request, 'products/templates/dashboard.html', {'products': products})


@method_decorator(csrf_exempt, name='dispatch')
class HTMXCreateProductView(View):
    """Captures form inputs from the browser frontend and writes them to the database"""
    def post(self, request):
        # Extract native string parameters from the browser form payload
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description', '')

        # CRITICAL VALIDATION: Ensure we don't save empty rows
        if not name or not price or not stock:
            return HttpResponse("Missing required form data fields.", status=400)

        # WRITE DIRECTLY TO THE SQL DATABASE
        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description
        )

        # Trigger your containerized Celery worker task asynchronously
        simulate_heavy_background_job.delay(product.name)

        # Render the fresh data row to send back to the user view screen
        context = {'product': product}
        html_row = render_to_string('products/templates/products/partials/product_row.html', context)
        return HttpResponse(html_row)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteProductView(View):
    """Locates a database item by its primary key (ID) and destroys the record"""
    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        if product:
            product.delete()
        
        # An empty response tells HTMX to completely remove the row from the screen
        return HttpResponse("")
