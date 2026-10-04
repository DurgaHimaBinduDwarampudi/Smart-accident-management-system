from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.user.username}"


class VehicleInsurance(models.Model):
    vehicle_number = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=100)
    insurance_company = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=50)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    vehicle_type = models.CharField(max_length=50, choices=[
        ('car', 'Car'),
        ('bike', 'Bike / Motorcycle'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('auto', 'Auto Rickshaw'),
    ], default='car')

    def __str__(self):
        return f"{self.vehicle_number} - {self.owner_name}"


class AccidentReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('analyzed', 'Analyzed'),
        ('claimed', 'Claim Submitted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accident_reports')
    image = models.ImageField(upload_to='accidents/')
    vehicle_number = models.CharField(max_length=20, blank=True)
    detected_vehicle_number = models.CharField(max_length=20, blank=True)
    report_date = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    emergency_alerts_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Report #{self.id} by {self.user.username} on {self.report_date.strftime('%Y-%m-%d')}"


class DamageAnalysis(models.Model):
    report = models.OneToOneField(AccidentReport, on_delete=models.CASCADE, related_name='damage_analysis')
    damaged_parts = models.JSONField(default=list)
    total_repair_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_coverage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    analysis_summary = models.TextField(blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Report #{self.report.id}"


class LoginOTP(models.Model):
    """Stores OTP for email-based login verification."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"OTP for {self.user.username} - {'Used' if self.is_used else 'Active'}"
