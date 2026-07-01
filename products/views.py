from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job
from django.shortcuts import render
from django.views import View

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