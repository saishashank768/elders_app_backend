from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Role, City, NGOProfile, Profile, CareRequest, VolunteerProfile, EmergencyContact
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data: roles, cities, sample users, requests'

    def handle(self, *args, **options):
        roles = ['donor','ngo','volunteer','elder','admin','csr']
        for r in roles:
            Role.objects.get_or_create(name=r)

        cities = [
            ('Mumbai','Maharashtra','India'),
            ('Delhi','Delhi','India'),
            ('Bengaluru','Karnataka','India')
        ]
        for name,state,country in cities:
            City.objects.get_or_create(name=name,state=state,country=country)

        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME','admin')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL','admin@example.com')
        admin_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD','adminpass')
        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(admin_username, admin_email, admin_pass)

        # sample NGO user
        ngo_user, _ = User.objects.get_or_create(username='sample_ngo', defaults={'email':'ngo@example.com'})
        ngo_profile_user = Profile.objects.get_or_create(user=ngo_user)[0]
        ngo_role = Role.objects.get(name='ngo')
        ngo_profile_user.role = ngo_role
        ngo_profile_user.save()
        NGOProfile.objects.get_or_create(profile=ngo_profile_user, org_name='Sample NGO')

        # sample volunteer
        vol_user, _ = User.objects.get_or_create(username='volunteer1', defaults={'email':'vol@example.com'})
        vol_profile = Profile.objects.get_or_create(user=vol_user)[0]
        vol_role = Role.objects.get(name='volunteer')
        vol_profile.role = vol_role
        vol_profile.save()
        VolunteerProfile.objects.get_or_create(profile=vol_profile, skills=['cooking'])

        # sample requests
        ngo = NGOProfile.objects.first()
        city = City.objects.first()
        for t in ['Food for 20 elderly','Medicine supply','Blood required']:
            CareRequest.objects.get_or_create(title=t, defaults={'description':'Sample','category':'food','urgency':'high','city':city,'ngo':ngo})

        self.stdout.write(self.style.SUCCESS('Seeded initial data'))
