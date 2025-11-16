from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator
from .validators import validate_file_size, validate_image_type

User = settings.AUTH_USER_MODEL


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, default='India')

    class Meta:
        unique_together = ('name', 'state')

    def __str__(self):
        return f"{self.name}, {self.state or self.country}"


class EmergencyContact(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    relation = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_file_size, validate_image_type])
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.user.username}"


class ElderProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='elder')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    mobility = models.CharField(max_length=120, blank=True)
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"ElderProfile: {self.profile.user.username}"


class VolunteerProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='volunteer')
    skills = models.JSONField(default=list, blank=True)
    availability = models.JSONField(default=dict, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Volunteer: {self.profile.user.username}"


class NGOProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='ngo')
    org_name = models.CharField(max_length=200)
    reg_number = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"NGO: {self.org_name}"


class CareRequest(models.Model):
    CATEGORY_CHOICES = [('food','food'),('medicine','medicine'),('blood','blood'),('others','others')]
    URGENCY_CHOICES = [('low','low'),('medium','medium'),('high','high')]
    STATUS_CHOICES = [('open','open'),('assigned','assigned'),('completed','completed'),('cancelled','cancelled')]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='others')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    quantity = models.IntegerField(default=1)
    location = models.CharField(max_length=255, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='requests/', null=True, blank=True, validators=[validate_file_size, validate_image_type])
    is_live = models.BooleanField(default=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_requests')
    elder_profile = models.ForeignKey(ElderProfile, on_delete=models.SET_NULL, null=True, blank=True)
    ngo = models.ForeignKey(NGOProfile, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['category','urgency','is_live','created_at'])]

    def __str__(self):
        return f"Request: {self.title} ({self.status})"


class Task(models.Model):
    STATUS_CHOICES = [('pending','pending'),('done','done')]
    request = models.ForeignKey(CareRequest, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    proof_file = models.FileField(upload_to='task_proofs/', null=True, blank=True, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','png'])])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task: {self.title} [{self.status}]"


class Payment(models.Model):
    donation = models.OneToOneField('Donation', on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    provider = models.CharField(max_length=120)
    provider_payment_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=50, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.provider_payment_id} ({self.status})"


class Donation(models.Model):
    STATUS_CHOICES = [('pledged','pledged'),('paid','paid'),('delivered','delivered')]
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='donations')
    ngo = models.ForeignKey(NGOProfile, on_delete=models.SET_NULL, null=True, blank=True)
    request = models.ForeignKey(CareRequest, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pledged')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation: {self.amount} by {self.donor}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    request = models.ForeignKey(CareRequest, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    attachment = models.FileField(upload_to='messages/', null=True, blank=True, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','png'])])
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or 'room'}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user} - {self.type}"


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    elder_profile = models.ForeignKey(ElderProfile, on_delete=models.SET_NULL, null=True, blank=True)
    file_path = models.FileField(upload_to='documents/', validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','png'])])
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=120, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document: {self.title} ({self.user})"


class Appointment(models.Model):
    elder = models.ForeignKey(ElderProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.title} at {self.scheduled_time}"


class Medication(models.Model):
    elder = models.ForeignKey(ElderProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255, blank=True)
    reminder_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Medication: {self.name} for {self.elder}"


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} - {self.rating}"
