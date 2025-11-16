from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser




# We use Django's User model. Profiles are in apps.core.Profile (OneToOne).
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True)
