from django.test import TestCase
from django.urls import reverse
# Create your tests here.

class HomeViewTestCase(TestCase):
    def test_home_view(self):
        # Get the URL for the 'home' view
        url = reverse('home')  # Assuming 'home' is the name of your view's URL pattern

        # Issue a GET request to the URL
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
