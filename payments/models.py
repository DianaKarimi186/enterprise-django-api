from django.db import models
from orders.models import Order


class Payment(models.Model):
    class Provider(models.TextChoices):
        STRIPE = "STRIPE", "Stripe"
        MPESA = "MPESA", "M-Pesa"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    transaction_reference = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.provider} - "
            f"{self.order.id} - "
            f"{self.status}"
        )