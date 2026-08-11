from unittest.mock import patch

from django.test import TestCase

from products.tasks import simulate_heavy_background_job


class CeleryTaskTests(TestCase):

    @patch("products.tasks.time.sleep")
    def test_simulate_heavy_background_job(self, mock_sleep):
        result = simulate_heavy_background_job("Test Product")

        self.assertEqual(
            result,
            "Processed Test Product",
        )

        mock_sleep.assert_called_once_with(10)