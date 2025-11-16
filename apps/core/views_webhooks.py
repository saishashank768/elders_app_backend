import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Donation, Payment, Notification
from django.utils import timezone


@csrf_exempt
def payment_webhook(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail':'invalid payload'}, status=400)

    provider = payload.get('provider')
    provider_payment_id = payload.get('provider_payment_id')
    donation_id = payload.get('donation_id')
    status = payload.get('status')

    try:
        donation = Donation.objects.get(id=donation_id)
    except Donation.DoesNotExist:
        return JsonResponse({'detail':'donation not found'}, status=404)

    # create or update payment
    payment, _ = Payment.objects.get_or_create(donation=donation, defaults={'provider': provider, 'provider_payment_id': provider_payment_id, 'amount': donation.amount, 'status': status or 'pending'})
    payment.status = status or payment.status
    if status == 'paid':
        donation.status = 'paid'
        payment.paid_at = timezone.now()
        donation.save()
    payment.save()

    # send notifications (create simple notification objects)
    Notification.objects.create(user=donation.donor, type='payment_update', payload={'status': payment.status})
    if donation.ngo and donation.ngo.profile and donation.ngo.profile.user:
        Notification.objects.create(user=donation.ngo.profile.user, type='donation_update', payload={'donation_id': donation.id, 'status': donation.status})

    return JsonResponse({'ok': True})
