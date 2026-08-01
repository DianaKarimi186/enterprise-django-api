from django.urls import path

from .views import (
    CartView,
    AddToCartView,
    RemoveFromCartView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart"),

    path(
        "add/<int:product_id>/",
        AddToCartView.as_view(),
        name="add-to-cart",
    ),

    path(
        "remove/<int:product_id>/",
        RemoveFromCartView.as_view(),
        name="remove-from-cart",
    ),
]