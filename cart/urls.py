from django.urls import path

from .views import CartView,AddToCartView,RemoveFromCartView,UpdateCartQuantityView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),

    path("add/<int:product_id>/",AddToCartView.as_view(),name="add-to-cart",),
    path("remove/<int:product_id>/",RemoveFromCartView.as_view(),name="remove-from-cart",),
    path("update/<int:product_id>/",UpdateCartQuantityView.as_view(),name="update-cart",),
]