from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User


class RegisterTests(APITestCase):

    def test_user_can_register(self):

        url = reverse("register")

        data = {
            "username": "john",
            "email": "john@example.com",
            "password": "Password123!"
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            User.objects.count(),
            1
        )

        self.assertEqual(
            User.objects.first().username,
            "john"
        )