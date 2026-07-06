from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job
from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@method_decorator(csrf_exempt, name='dispatch')
class HTMXCreateProductView(View):
    def post(self, request):
        # Extract the native form fields sent by the browser
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description', '')

        # Insert record safely into the database table
        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description
        )

        # Trigger your Celery task asynchronously in the background!
        simulate_heavy_background_job.delay(product.name)

        # Render JUST a single partial table row to send back to HTMX
        context = {'product': product}
        html_row = render_to_string('templates/products/partials/product_row.html', context)
        return HttpResponse(html_row)
    
@method_decorator(csrf_exempt, name='dispatch')
class DeleteProductView(View):
    def delete(self, request, pk):
        # Locate the specific item using its database primary key (pk)
        product = Product.objects.filter(pk=pk).first()
        if product:
            product.delete()
        
        # Return an empty string. When HTMX receives a 200 OK with no text,
        # it automatically removes that row from the screen!
        return HttpResponse("")


class ProductListCreateView(generics.ListCreateAPIView):
    # OPTIMIZATION FIX: select_related performs a SQL JOIN to pull categories instantly in 1 query!
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        simulate_heavy_background_job.delay(instance.name)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    # OPTIMIZATION FIX: Optimized single item lookup queries
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
class DashboardView(View):
    def get(self, request):
        products = Product.objects.select_related('category').all()
        return render(request, 'products/dashboard.html', {
            'products': products
        })