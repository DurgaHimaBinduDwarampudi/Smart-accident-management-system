from django.contrib import admin
from .models import UserProfile, EmergencyContact, VehicleInsurance, AccidentReport, DamageAnalysis, LoginOTP


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'phone', 'email', 'user']
    list_filter = ['relationship']
    search_fields = ['name', 'phone', 'email', 'user__username']


@admin.register(VehicleInsurance)
class VehicleInsuranceAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'owner_name', 'insurance_company', 'expiry_date', 'vehicle_type']
    search_fields = ['vehicle_number', 'owner_name']
    list_filter = ['vehicle_type']


@admin.register(AccidentReport)
class AccidentReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'vehicle_number', 'report_date', 'status', 'emergency_alerts_sent']
    list_filter = ['status', 'emergency_alerts_sent']
    search_fields = ['user__username', 'vehicle_number']


@admin.register(DamageAnalysis)
class DamageAnalysisAdmin(admin.ModelAdmin):
    list_display = ['report', 'total_repair_cost', 'insurance_coverage', 'payable_amount', 'analyzed_at']


@admin.register(LoginOTP)
class LoginOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used']
    search_fields = ['user__username']
    readonly_fields = ['otp_code', 'created_at', 'expires_at']
