from django.contrib import admin
from .models import Role, City, Profile, ElderProfile, VolunteerProfile, NGOProfile, CareRequest, Task, Donation, Payment, Message, Notification, Document, Appointment, Medication, Feedback, EmergencyContact

models = [Role, City, Profile, ElderProfile, VolunteerProfile, NGOProfile, CareRequest, Task, Donation, Payment, Message, Notification, Document, Appointment, Medication, Feedback, EmergencyContact]

for m in models:
    admin.site.register(m)
