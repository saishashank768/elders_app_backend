from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.core.models import Role, City

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Role.objects.create(name='donor')
        City.objects.create(name='TestCity')

    def test_public_requests_list(self):
        url = reverse('requests-list')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
