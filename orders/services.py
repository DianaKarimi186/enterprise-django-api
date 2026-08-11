from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem


@transaction.atomic
def checkout(user):
    cart = get_object_or_404(Cart, user=user)

    if not cart.items.exists():
        raise ValueError("Your cart is empty.")

    order = Order.objects.create(user=user)

    total = Decimal("0.00")

    for item in cart.items.select_related("product"):
        product = item.product

        if item.quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} item(s) available for {product.name}."
            )

        subtotal = product.price * item.quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=product.price,
            subtotal=subtotal,
        )

        product.stock -= item.quantity
        product.save()

        total += subtotal

    order.total = total
    order.save()

    cart.items.all().delete()

    return order