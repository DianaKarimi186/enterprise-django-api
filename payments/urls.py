from django.urls import path

from .views import (
    PaymentListView,
    PaymentDetailView,
    ProcessPaymentView,
)

urlpatterns = [
    path(
        "",
        PaymentListView.as_view(),
        name="payment-list",
    ),
    path(
        "<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path(
        "process/<int:order_id>/",
        ProcessPaymentView.as_view(),
        name="process-payment",
    ),
]