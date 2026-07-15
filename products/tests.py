from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product

from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext

from django.core.cache import cache

from .models import Product, Category


from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext

from .models import Product, Category


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




class ProductQueryPerformanceTest(TestCase):

    def setUp(self):
        category = Category.objects.create(
            name="Electronics"
        )

        for index in range(10):
            Product.objects.create(
                category=category,
                name=f"Product {index}",
                price=100,
                stock=10
            )

    def test_unoptimized_product_queries(self):
        with CaptureQueriesContext(connection) as queries:
            products = Product.objects.all()

            for product in products:
                _ = product.category.name

        self.assertEqual(len(queries), 11)

    def test_optimized_product_queries(self):
        with CaptureQueriesContext(connection) as queries:
            products = Product.objects.select_related(
                "category"
            )

            for product in products:
                _ = product.category.name

        self.assertEqual(len(queries), 1)


class ProductCacheTest(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_product_cache_can_store_data(self):
        products = ["Keyboard", "Monitor"]

        cache.set(
            "inventory_products",
            products,
            timeout=300
        )

        cached_products = cache.get(
            "inventory_products"
        )

        self.assertEqual(
            cached_products,
            products
        )

    def test_inventory_cache_can_be_invalidated(self):
        cache.set(
            "inventory_products",
            ["Old Product"],
            timeout=300
        )

        cache.delete("inventory_products")

        cached_products = cache.get(
            "inventory_products"
        )

        self.assertIsNone(cached_products)

class ProductCacheSignalTest(TestCase):

    CACHE_KEY = "inventory_products"

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def populate_cache(self):
        cache.set(
            self.CACHE_KEY,
            ["Cached Product"],
            timeout=300
        )

    def test_product_create_invalidates_cache(self):
        self.populate_cache()

        Product.objects.create(
            name="Laptop",
            price="1500.00",
            stock=5
        )

        self.assertIsNone(
            cache.get(self.CACHE_KEY)
        )

    def test_product_update_invalidates_cache(self):
        product = Product.objects.create(
            name="Laptop",
            price="1500.00",
            stock=5
        )

        self.populate_cache()

        product.stock = 10
        product.save()

        self.assertIsNone(
            cache.get(self.CACHE_KEY)
        )

    def test_product_delete_invalidates_cache(self):
        product = Product.objects.create(
            name="Laptop",
            price="1500.00",
            stock=5
        )

        self.populate_cache()

        product.delete()

        self.assertIsNone(
            cache.get(self.CACHE_KEY)
        )