from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category, Product
from cart.models import Cart, CartItem

User = get_user_model()

class CartTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="diana",
            password="testpass123"
        )

        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Electronics"
        )

        self.product = Product.objects.create(
            category=self.category,
            owner=self.user,
            name="Phone",
            description="Smart phone",
            price=1000,
            stock=10,
        )
    def test_get_empty_cart(self):
        response = self.client.get("/api/cart/")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["items"],
           [],
        )

    def test_get_empty_cart(self):
        response = self.client.get("/api/cart/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["items"],
            [],
        )
    def test_add_product_to_cart(self):
        response = self.client.post(
            f"/api/cart/add/{self.product.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        cart = Cart.objects.get(user=self.user)

        self.assertEqual(
            cart.items.count(),
            1,
        )
        def test_update_cart_quantity(self):
            self.client.post(
                f"/api/cart/add/{self.product.id}/"
            )

            response = self.client.patch(
                f"/api/cart/update/{self.product.id}/",
                {
                    "quantity": 3
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

            item = CartItem.objects.get(
                product=self.product
            )

            self.assertEqual(
                item.quantity,
                3,
            )

        def test_remove_product_from_cart(self):
            self.client.post(
                f"/api/cart/add/{self.product.id}/"
            )

            response = self.client.delete(
                f"/api/cart/remove/{self.product.id}/"
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_204_NO_CONTENT,
            )

            cart = Cart.objects.get(user=self.user)

            self.assertEqual(
                cart.items.count(),
                0,
            )
        def test_update_quantity_requires_quantity(self):
            self.client.post(
                f"/api/cart/add/{self.product.id}/"
            )

            response = self.client.patch(
                f"/api/cart/update/{self.product.id}/",
                {},
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
        def test_quantity_cannot_be_zero(self):
            self.client.post(
                f"/api/cart/add/{self.product.id}/"
            )

            response = self.client.patch(
                f"/api/cart/update/{self.product.id}/",
                {
                    "quantity": 0
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
        def test_anonymous_user_cannot_access_cart(self):
            self.client.logout()

            response = self.client.get("/api/cart/")

            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
            )
        