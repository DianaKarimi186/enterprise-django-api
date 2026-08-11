from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Category, Product


class ProductTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            password="Password123!"
        )

        token = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token.access_token}"
        )

        self.category = Category.objects.create(
            name="Electronics"
        )

    def test_create_product(self):
        response = self.client.post(
            "/api/products/",
            {
                "category": self.category.id,
                "name": "Laptop",
                "description": "Gaming laptop",
                "price": 1500,
                "stock": 5
            },
            format="json"
        )

        print("STATUS:", response.status_code)
        print("DATA:", response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Product.objects.count(),
            1
        )

        self.assertEqual(
            Product.objects.first().owner,
            self.user
        )