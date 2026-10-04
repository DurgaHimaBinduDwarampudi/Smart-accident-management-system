from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('login/verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/resend-otp/', views.resend_otp, name='resend_otp'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Profile & Emergency Contacts
    path('profile/', views.profile_view, name='profile'),
    path('emergency-contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('emergency-contacts/add/', views.add_emergency_contact, name='add_emergency_contact'),
    path('emergency-contacts/delete/<int:pk>/', views.delete_emergency_contact, name='delete_emergency_contact'),

    # Accident Reporting
    path('report/', views.upload_accident, name='upload_accident'),
    path('report/<int:report_id>/analyze/', views.analyze_damage, name='analyze_damage'),
    path('report/<int:report_id>/result/', views.view_result, name='view_result'),
    path('report/<int:report_id>/send-alert/', views.send_emergency_alert, name='send_emergency_alert'),
    path('reports/', views.my_reports, name='my_reports'),

    # Nearby Services
    path('report/<int:report_id>/nearby/', views.nearby_services, name='nearby_services'),

    # Insurance
    path('insurance/check/', views.check_insurance, name='check_insurance'),

    # Admin - Manage Insurance DB
    path('admin-panel/insurance/', views.manage_insurance, name='manage_insurance'),
    path('admin-panel/insurance/add/', views.add_insurance, name='add_insurance'),
]
