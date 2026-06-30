from rest_framework import serializers
from .models import Product

# Check every letter: ProductSerializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at']
