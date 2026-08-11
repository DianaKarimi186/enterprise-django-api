from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "subtotal",
        ]


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    items = CartItemSerializer(
        many=True,
        read_only=True
    )

    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "total",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["total"] = sum(
            item.subtotal
            for item in instance.items.all()
        )

        return data