from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
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

        self.client.force_login(self.user)

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

    @patch("products.views.simulate_heavy_background_job.delay")
    def test_htmx_create_product(self, mock_task):
        response = self.client.post(
            "/api/products/dashboard/create/",
            {
                "category": self.category.id,
                "name": "HTMX Laptop",
                "description": "Created through HTMX",
                "price": "1200.00",
                "stock": "10",
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            Product.objects.count(),
            1
        )

        product = Product.objects.first()

        self.assertEqual(
            product.name,
            "HTMX Laptop"
        )

        self.assertEqual(
            product.owner,
            self.user
        )

        self.assertEqual(
            product.category,
            self.category
        )

        mock_task.assert_called_once_with(
            "HTMX Laptop"
        )

    @patch("products.views.simulate_heavy_background_job.delay")
    def test_htmx_create_product_requires_category(self, mock_task):
        response = self.client.post(
            "/api/products/dashboard/create/",
            {
                "name": "Laptop",
                "description": "Missing category",
                "price": "1200.00",
                "stock": "10",
            }
        )

        self.assertEqual(
            response.status_code,
            422
        )

        self.assertEqual(
            Product.objects.count(),
            0
        )

        mock_task.assert_not_called()

    @patch("products.views.simulate_heavy_background_job.delay")
    def test_htmx_create_product_rejects_invalid_price(self, mock_task):
        response = self.client.post(
            "/api/products/dashboard/create/",
            {
                "category": self.category.id,
                "name": "Laptop",
                "description": "Invalid price",
                "price": "0",
                "stock": "10",
            }
        )

        self.assertEqual(
            response.status_code,
            422
        )

        self.assertEqual(
            Product.objects.count(),
            0
        )

        mock_task.assert_not_called()

    @patch("products.views.simulate_heavy_background_job.delay")
    def test_htmx_create_product_rejects_negative_stock(self, mock_task):
        response = self.client.post(
            "/api/products/dashboard/create/",
            {
                "category": self.category.id,
                "name": "Laptop",
                "description": "Invalid stock",
                "price": "1200.00",
                "stock": "-1",
            }
        )

        self.assertEqual(
            response.status_code,
            422
        )

        self.assertEqual(
            Product.objects.count(),
            0
        )

        mock_task.assert_not_called()

    @patch("products.views.simulate_heavy_background_job.delay")
    def test_process_product_starts_background_task(self, mock_task):
        product = Product.objects.create(
            owner=self.user,
            category=self.category,
            name="Process Laptop",
            description="Product to process",
            price="1500.00",
            stock=5,
        )

        mock_task.return_value.id = "test-task-id-123"

        response = self.client.post(
            f"/api/products/{product.id}/process/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED
        )

        self.assertEqual(
            response.data["message"],
            "Product processing started"
        )

        self.assertEqual(
            response.data["task_id"],
            "test-task-id-123"
        )

        self.assertEqual(
            response.data["product_id"],
            product.id
        )

        self.assertEqual(
            response.data["product_name"],
            "Process Laptop"
        )

        mock_task.assert_called_once_with(
            "Process Laptop"
        )
    @patch("products.views.AsyncResult")
    def test_task_status_pending(self, mock_async_result):
        mock_task = mock_async_result.return_value

        mock_task.id = "test-task-id-123"
        mock_task.status = "PENDING"
        mock_task.successful.return_value = False

        response = self.client.get(
            "/api/products/tasks/test-task-id-123/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["task_id"],
            "test-task-id-123"
        )

        self.assertEqual(
            response.data["status"],
            "PENDING"
        )

        self.assertIsNone(
            response.data["result"]
        )

        mock_async_result.assert_called_once_with(
            "test-task-id-123"
        )


    @patch("products.views.AsyncResult")
    def test_task_status_success(self, mock_async_result):
        mock_task = mock_async_result.return_value

        mock_task.id = "test-task-id-456"
        mock_task.status = "SUCCESS"
        mock_task.successful.return_value = True
        mock_task.result = "Processed Test Product"

        response = self.client.get(
            "/api/products/tasks/test-task-id-456/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["task_id"],
            "test-task-id-456"
        )

        self.assertEqual(
            response.data["status"],
            "SUCCESS"
        )

        self.assertEqual(
            response.data["result"],
            "Processed Test Product"
        )

        mock_async_result.assert_called_once_with(
            "test-task-id-456"
        )