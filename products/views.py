from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        simulate_heavy_background_job.delay(instance.name)



class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
