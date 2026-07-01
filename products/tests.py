from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product

class ProductAPITests(APITestCase):

    def setUp(self):
        # This setup function runs before every single test case to populate data
        self.list_create_url = reverse('product-list-create')
        self.sample_product = Product.objects.create(
            name="Test Drone",
            description="Testing automated loops",
            price=299.99,
            stock=5
        )

    def test_public_can_read_products_list(self):
        """Verify that any anonymous user can perform a GET request on products"""
        response = self.client.get(self.list_create_url)
        
        # We assert (expect) that the server responds with a 200 OK code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that our sample product is included in the returned data array
        self.assertEqual(len(response.data), 1)

    def test_anonymous_user_cannot_create_product(self):
        """Verify that our security layer blocks POST requests without a JWT token"""
        data = {
            "name": "Hacker Laptop",
            "price": 1200.00,
            "stock": 1
        }
        response = self.client.post(self.list_create_url, data, format='json')
        
        # We assert that the server correctly blocks the request with a 403 Forbidden code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
