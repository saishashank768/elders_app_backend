from celery import shared_task
from django.utils import timezone
from .models import Medication, Appointment, CareRequest, Notification


@shared_task
def send_medication_reminders():
    now = timezone.now()
    meds = Medication.objects.exclude(reminder_time=None)
    for m in meds:
        # placeholder: logic to match current time
        Notification.objects.create(user=m.elder.profile.user, type='medication_reminder', payload={'medication': m.name})


@shared_task
def send_appointment_reminders():
    now = timezone.now()
    upcoming = Appointment.objects.filter(scheduled_time__gte=now)
    for appt in upcoming:
        Notification.objects.create(user=appt.elder.profile.user, type='appointment_reminder', payload={'appointment': appt.title})


@shared_task
def daily_digest():
    # create a simple digest for each city
    cities = set(CareRequest.objects.values_list('city', flat=True))
    for city_id in cities:
        requests = CareRequest.objects.filter(city_id=city_id, created_at__date=timezone.now().date())
        if requests.exists():
            # notify admin / city contacts - simplified
            pass
