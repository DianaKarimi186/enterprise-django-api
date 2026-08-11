from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTests(APITestCase):

    def setUp(self):
        User.objects.create_user(
            username="john",
            password="Password123!"
        )

    def test_user_can_login(self):
        url = reverse("login")

        response = self.client.post(
            url,
            {
                "username": "john",
                "password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)