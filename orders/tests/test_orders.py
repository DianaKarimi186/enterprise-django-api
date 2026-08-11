from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from orders.models import Order
from products.models import Product, Category


class OrderTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!"
        )

        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Electronics"
        )

        self.product = Product.objects.create(
            name="Laptop",
            description="Gaming laptop",
            price=Decimal("1500.00"),
            stock=5,
            category=self.category,
            owner=self.user,
        )

        self.cart = Cart.objects.create(
            user=self.user
        )

    def test_checkout_creates_order(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Order.objects.count(),
            1
        )

        order = Order.objects.first()

        self.assertEqual(
            order.user,
            self.user
        )

        self.assertEqual(
            order.total,
            Decimal("3000.00")
        )

    def test_checkout_reduces_stock(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            3
        )

    def test_checkout_clears_cart(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            self.cart.items.count(),
            0
        )

    def test_checkout_fails_when_cart_is_empty(self):
        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["error"],
            "Your cart is empty."
        )

    def test_checkout_fails_when_stock_is_insufficient(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=10,
        )

        response = self.client.post(
            "/api/orders/checkout/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Only 5 item(s) available",
            response.data["error"]
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            5
        )

        self.assertEqual(
            Order.objects.count(),
            0
        )
    def test_user_can_list_orders(self):
        order = Order.objects.create(
            user=self.user,
            total=Decimal("1500.00")
        )

        response = self.client.get(
            "/api/orders/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data["results"]),
            1
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            order.id
        )


    def test_user_can_retrieve_own_order(self):
        order = Order.objects.create(
            user=self.user,
            total=Decimal("1500.00")
        )

        response = self.client.get(
            f"/api/orders/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            order.id
        )


    def test_user_cannot_retrieve_another_users_order(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            password="TestPassword123!"
        )

        order = Order.objects.create(
            user=another_user,
            total=Decimal("1500.00")
        )

        response = self.client.get(
            f"/api/orders/{order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
    def test_admin_can_update_order_status(self):
        admin = User.objects.create_user(
            username="admin",
            password="AdminPassword123!",
            is_staff=True,
            is_superuser=True,
        )

        order = Order.objects.create(
            user=self.user,
            total=Decimal("1500.00")
        )

        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            f"/api/orders/{order.id}/status/",
            {
                "status": "PAID"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PAID
        )


    def test_regular_user_cannot_update_order_status(self):
        order = Order.objects.create(
            user=self.user,
            total=Decimal("1500.00")
        )

        response = self.client.patch(
            f"/api/orders/{order.id}/status/",
            {
                "status": "PAID"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PENDING
        )


    def test_invalid_order_status_is_rejected(self):
        admin = User.objects.create_user(
            username="admin",
            password="AdminPassword123!",
            is_staff=True,
            is_superuser=True,
        )

        order = Order.objects.create(
            user=self.user,
            total=Decimal("1500.00")
        )

        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            f"/api/orders/{order.id}/status/",
            {
                "status": "INVALID_STATUS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["error"],
            "Invalid status."
        )