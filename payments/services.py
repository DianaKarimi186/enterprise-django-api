import uuid

from .models import Payment
from orders.models import Order


def process_payment(order: Order, provider: str) -> Payment:
    """
    Simulates a successful payment.
    Later this function will integrate with Stripe or M-Pesa.
    """

    payment = Payment.objects.create(
        order=order,
        provider=provider,
        amount=order.total,
        status=Payment.Status.SUCCESS,
        transaction_reference=str(uuid.uuid4()),
    )

    order.status = Order.Status.PAID
    order.save(update_fields=["status"])

    return payment