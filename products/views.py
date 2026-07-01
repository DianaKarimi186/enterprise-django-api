from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job

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
