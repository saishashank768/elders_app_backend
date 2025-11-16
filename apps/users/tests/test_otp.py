from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.cache import cache


class OTPTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_and_verify_otp(self):
        url = reverse('send-otp')
        r = self.client.post(url, {'phone': '+919876543210'}, format='json')
        self.assertEqual(r.status_code, 200)
        token = r.data.get('otp_token')
        self.assertTrue(token)
        # fetch OTP from cache (since dev logs it)
        otp = cache.get(f'otp:{token}')
        self.assertTrue(otp)
        r2 = self.client.post(reverse('verify-otp'), {'otp_token': token, 'otp': otp}, format='json')
        self.assertEqual(r2.status_code, 200)
