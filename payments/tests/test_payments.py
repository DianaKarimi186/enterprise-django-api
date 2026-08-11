from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order
from payments.models import Payment


class PaymentTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="paymentuser",
            password="TestPassword123!"
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.order = Order.objects.create(
            user=self.user,
            status=Order.Status.PENDING,
            total=Decimal("1500.00"),
        )

    def test_successful_stripe_payment(self):
        response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {
                "provider": "STRIPE"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["order"],
            self.order.id
        )

        self.assertEqual(
            response.data["provider"],
            "STRIPE"
        )

        self.assertEqual(
            response.data["amount"],
            "1500.00"
        )

        self.assertEqual(
            response.data["status"],
            "SUCCESS"
        )

        self.assertTrue(
            response.data["transaction_reference"]
        )

    def test_payment_changes_order_status_to_paid(self):
        response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {
                "provider": "STRIPE"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.Status.PAID
        )

    def test_payment_amount_matches_order_total(self):
        response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {
                "provider": "MPESA"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertEqual(
            payment.amount,
            self.order.total
        )

    def test_missing_provider_is_rejected(self):
        response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["error"],
            "Provider is required."
        )

        self.assertEqual(
            Payment.objects.count(),
            0
        )

    def test_duplicate_payment_is_rejected(self):
        first_response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {
                "provider": "STRIPE"
            },
            format="json"
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )

        second_response = self.client.post(
            f"/api/payments/process/{self.order.id}/",
            {
                "provider": "STRIPE"
            },
            format="json"
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            second_response.data["error"],
            "Payment already exists."
        )

        self.assertEqual(
            Payment.objects.count(),
            1
        )