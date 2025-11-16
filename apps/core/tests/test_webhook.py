from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.core.models import Donation

User = get_user_model()


class WebhookTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='donor1')
        self.donation = Donation.objects.create(donor=self.user, amount=1000)

    def test_webhook_updates_payment(self):
        url = reverse('payment-webhook')
        payload = {'provider':'razorpay','provider_payment_id':'pay_ABC','donation_id': self.donation.id,'status':'paid'}
        r = self.client.post(url, payload, format='json')
        self.assertEqual(r.status_code, 200)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, 'paid')
