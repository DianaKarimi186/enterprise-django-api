from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from products.models import Product


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def add_to_cart(user, product_id):
    cart = get_or_create_cart(user)

    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if created:
        if product.stock < 1:
            item.delete()
            raise ValueError("This product is out of stock.")

        return item

    if item.quantity >= product.stock:
        raise ValueError(
            f"Only {product.stock} item(s) are available in stock."
        )

    item.quantity += 1
    item.save()

    return item


def update_quantity(user, product_id, quantity):
    cart = get_or_create_cart(user)

    item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id,
    )

    if quantity > item.product.stock:
        raise ValueError(
            f"Only {item.product.stock} item(s) are available in stock."
        )

    item.quantity = quantity
    item.save()

    return item


def remove_from_cart(user, product_id):
    cart = get_or_create_cart(user)

    item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id,
    )

    item.delete()