from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from .models import UserProfile, EmergencyContact, VehicleInsurance, AccidentReport, DamageAnalysis, LoginOTP
from .forms import (UserRegistrationForm, UserLoginForm, EmergencyContactForm,
                    AccidentReportForm, InsuranceForm, UserProfileForm, OTPVerificationForm)
from .utils import (analyze_vehicle_damage, extract_number_plate,
                    get_nearby_hospitals, get_nearby_service_centers,
                    send_emergency_email, send_emergency_sms,
                    send_otp_sms, send_otp_email, mask_phone)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _create_and_send_otp(request, user, profile):
    """
    Invalidate old OTPs, create a new one, send via SMS (Twilio) if configured,
    otherwise fall back to email OTP. Returns (sent: bool, method: str).
    """
    LoginOTP.objects.filter(user=user, is_used=False).update(is_used=True)
    otp_code = LoginOTP.generate_otp()
    expiry = timezone.now() + timezone.timedelta(
        minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
    )
    LoginOTP.objects.create(user=user, otp_code=otp_code, expires_at=expiry)
    request.session['otp_user_id'] = user.id
    request.session['otp_attempts'] = 0

    # Try SMS first
    if getattr(settings, 'TWILIO_SMS_ENABLED', False) and profile.phone_number:
        if send_otp_sms(profile.phone_number, otp_code):
            return True, 'sms'

    # Fall back to email OTP
    if user.email:
        if send_otp_email(user.email, otp_code, user.first_name or user.username):
            return True, 'email'

    return False, 'none'


# ──────────────────────────────────────────────
# PUBLIC VIEWS
# ──────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accident_app/home.html')


def login_view(request):
    """
    Login with username + password.
    OTP is attempted as an optional second factor — if OTP cannot be sent
    (email/SMS not configured), the user is logged in directly so they are
    never locked out of their own account.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, 'Invalid username or password. Please check and try again.')
            return render(request, 'accident_app/login.html', {'form': form})

        # Ensure profile exists
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        # ── OTP step (optional) ──────────────────────────────
        # Only attempt OTP if phone or email is configured AND
        # Twilio or email backend is working.
        # If OTP cannot be sent → log the user in directly (password already verified).
        has_contact = bool(profile.phone_number or user.email)

        if has_contact:
            sent, method = _create_and_send_otp(request, user, profile)
            if sent:
                request.session['otp_method'] = method
                if method == 'sms':
                    masked = mask_phone(profile.phone_number)
                    messages.success(request, f'OTP sent via SMS to {masked}')
                else:
                    masked_email = user.email[:3] + '****' + user.email[user.email.index('@'):]
                    messages.success(request, f'OTP sent via email to {masked_email}')
                return redirect('verify_otp')
            else:
                # OTP send failed — still allow login (password already verified above)
                login(request, user)
                messages.success(
                    request,
                    f'Welcome back, {user.first_name or user.username}! '
                    f'(OTP skipped — email/SMS not configured.)'
                )
                return redirect('dashboard')
        else:
            # No contact info at all — skip OTP entirely
            login(request, user)
            messages.success(
                request,
                f'Welcome back, {user.first_name or user.username}! '
                f'Tip: add your email in Profile for extra security.'
            )
            return redirect('dashboard')

    return render(request, 'accident_app/login.html', {'form': form})


def verify_otp(request):
    """Step 2: user enters the OTP received on their mobile number."""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Invalid session. Please login again.')
        return redirect('login')

    max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 3)
    attempts = request.session.get('otp_attempts', 0)

    if attempts >= max_attempts:
        LoginOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        request.session.pop('otp_user_id', None)
        request.session.pop('otp_attempts', None)
        messages.error(request, 'Too many incorrect attempts. Please login again.')
        return redirect('login')

    form = OTPVerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        entered = form.cleaned_data['otp_code']
        otp_obj = (
            LoginOTP.objects
            .filter(user=user, is_used=False)
            .order_by('-created_at')
            .first()
        )

        if otp_obj and not otp_obj.is_valid():
            # OTP expired — clean up and redirect
            otp_obj.is_used = True
            otp_obj.save()
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_attempts', None)
            messages.error(request, 'OTP has expired. Please login again to get a new OTP.')
            return redirect('login')

        if otp_obj and otp_obj.otp_code == entered:
            otp_obj.is_used = True
            otp_obj.save()
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_attempts', None)
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 🎉')
            return redirect('dashboard')
        else:
            request.session['otp_attempts'] = attempts + 1
            remaining = max_attempts - request.session['otp_attempts']
            messages.error(request, f'Incorrect OTP. {remaining} attempt(s) remaining.')

    masked = mask_phone(profile.phone_number) if profile.phone_number else ''
    otp_method = request.session.get('otp_method', 'sms')
    masked_email = ''
    if otp_method == 'email' and user.email:
        masked_email = user.email[:3] + '****' + user.email[user.email.index('@'):]
    return render(request, 'accident_app/verify_otp.html', {
        'form': form,
        'masked_phone': masked,
        'masked_email': masked_email,
        'otp_method': otp_method,
        'otp_expiry': getattr(settings, 'OTP_EXPIRY_MINUTES', 10),
    })


def resend_otp(request):
    """Resend a fresh OTP to the user's mobile number."""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return redirect('login')

    sent, method = _create_and_send_otp(request, user, profile)
    request.session['otp_method'] = method
    if sent and method == 'sms':
        messages.success(request, f'New OTP sent via SMS to {mask_phone(profile.phone_number)}')
    elif sent and method == 'email':
        masked_email = user.email[:3] + '****' + user.email[user.email.index('@'):]
        messages.success(request, f'New OTP sent via email to {masked_email}')
    else:
        messages.error(request, 'Failed to resend OTP. Configure email or Twilio in settings.py.')

    return redirect('verify_otp')


def register_view(request):
    """Register new user — phone number and email are mandatory."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Save phone number to profile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'phone_number': form.cleaned_data['phone_number']},
        )

        # Auto-login after registration (no OTP needed — they just created the account)
        login(request, user)
        messages.success(
            request,
            f'Welcome, {user.first_name or user.username}! '
            f'Your account is set up. Next time you login, an OTP will be sent to '
            f'{mask_phone(form.cleaned_data["phone_number"])}.'
        )
        return redirect('dashboard')

    return render(request, 'accident_app/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    reports = AccidentReport.objects.filter(user=request.user).order_by('-report_date')
    contacts_count = EmergencyContact.objects.filter(user=request.user).count()
    total_reports = AccidentReport.objects.filter(user=request.user).count()
    return render(request, 'accident_app/dashboard.html', {
        'reports': reports,
        'contacts_count': contacts_count,
        'total_reports': total_reports,
    })


# ──────────────────────────────────────────────
# PROFILE
# ──────────────────────────────────────────────

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name  = request.POST.get('last_name',  request.user.last_name)
        request.user.email      = request.POST.get('email',      request.user.email)
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accident_app/profile.html', {'form': form, 'profile': profile})


# ──────────────────────────────────────────────
# EMERGENCY CONTACTS
# ──────────────────────────────────────────────

@login_required
def emergency_contacts(request):
    contacts = EmergencyContact.objects.filter(user=request.user)
    return render(request, 'accident_app/emergency_contacts.html', {'contacts': contacts})


@login_required
def add_emergency_contact(request):
    form = EmergencyContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        contact = form.save(commit=False)
        contact.user = request.user
        contact.save()
        messages.success(request, f'Emergency contact "{contact.name}" added!')
        return redirect('emergency_contacts')
    return render(request, 'accident_app/add_contact.html', {'form': form})


@login_required
def delete_emergency_contact(request, pk):
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Emergency contact removed.')
    return redirect('emergency_contacts')


# ──────────────────────────────────────────────
# ACCIDENT REPORTING & ANALYSIS
# ──────────────────────────────────────────────

@login_required
def upload_accident(request):
    form = AccidentReportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.user = request.user
        report.save()
        messages.info(request, 'Image uploaded. Running damage analysis...')
        return redirect('analyze_damage', report_id=report.id)
    return render(request, 'accident_app/upload_accident.html', {
        'form': form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })


@login_required
def analyze_damage(request, report_id):
    report = get_object_or_404(AccidentReport, id=report_id, user=request.user)

    # OCR number plate
    detected_plate = extract_number_plate(report.image.path)
    if detected_plate:
        report.detected_vehicle_number = detected_plate
        report.save(update_fields=['detected_vehicle_number'])

    # Damage analysis
    damaged_parts, total_cost, summary = analyze_vehicle_damage(report.image.path)

    # Check insurance coverage
    insurance_coverage = 0
    plate = report.vehicle_number or detected_plate
    if plate:
        try:
            ins = VehicleInsurance.objects.get(vehicle_number__iexact=plate)
            insurance_coverage = float(ins.coverage_amount)
        except VehicleInsurance.DoesNotExist:
            pass

    payable = max(0, total_cost - insurance_coverage)

    # Save analysis — explicit get/save to avoid SQLite select_for_update lock
    try:
        analysis = DamageAnalysis.objects.get(report=report)
        analysis.damaged_parts      = damaged_parts
        analysis.total_repair_cost  = total_cost
        analysis.insurance_coverage = insurance_coverage
        analysis.payable_amount     = payable
        analysis.analysis_summary   = summary
        analysis.save()
    except DamageAnalysis.DoesNotExist:
        DamageAnalysis.objects.create(
            report=report,
            damaged_parts=damaged_parts,
            total_repair_cost=total_cost,
            insurance_coverage=insurance_coverage,
            payable_amount=payable,
            analysis_summary=summary,
        )

    report.status = 'analyzed'
    report.save(update_fields=['status'])

    messages.success(request, 'Damage analysis complete!')
    return redirect('view_result', report_id=report.id)


@login_required
def view_result(request, report_id):
    report   = get_object_or_404(AccidentReport, id=report_id, user=request.user)
    analysis = get_object_or_404(DamageAnalysis, report=report)
    contacts = EmergencyContact.objects.filter(user=request.user)
    return render(request, 'accident_app/result.html', {
        'report':              report,
        'analysis':            analysis,
        'contacts':            contacts,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })


@login_required
def send_emergency_alert(request, report_id):
    """Send SMS + email alert to all emergency contacts."""
    report   = get_object_or_404(AccidentReport, id=report_id, user=request.user)
    contacts = EmergencyContact.objects.filter(user=request.user)

    if not contacts.exists():
        messages.warning(request, 'No emergency contacts found. Please add contacts first.')
        return redirect('emergency_contacts')

    email_sent_to = []
    sms_sent_to   = []
    sms_disabled  = not getattr(settings, 'TWILIO_SMS_ENABLED', False)

    for contact in contacts:
        if send_emergency_email(request.user, contact, report):
            email_sent_to.append(contact.email)
        if send_emergency_sms(request.user, contact, report):
            sms_sent_to.append(contact.phone)

    if email_sent_to or sms_sent_to:
        report.emergency_alerts_sent = True
        report.save(update_fields=['emergency_alerts_sent'])
        parts = []
        if email_sent_to:
            parts.append(f'📧 Email → {", ".join(email_sent_to)}')
        if sms_sent_to:
            parts.append(f'📱 SMS → {", ".join(sms_sent_to)}')
        elif sms_disabled:
            parts.append('(SMS disabled — configure Twilio in settings.py to enable)')
        messages.success(request, ' | '.join(parts))
    else:
        messages.error(request, 'Failed to send any alerts. Check email and Twilio configuration.')

    return redirect('view_result', report_id=report.id)


@login_required
def my_reports(request):
    reports = AccidentReport.objects.filter(user=request.user).order_by('-report_date')
    return render(request, 'accident_app/my_reports.html', {'reports': reports})


# ──────────────────────────────────────────────
# NEARBY SERVICES
# ──────────────────────────────────────────────

@login_required
def nearby_services(request, report_id):
    report = get_object_or_404(AccidentReport, id=report_id, user=request.user)
    # Pass exact coordinates to the template.
    # All place searching is done client-side via Google Maps JS API (or Overpass
    # fallback), so no server-side fetch is needed here.
    lat = float(report.latitude or 0)
    lon = float(report.longitude or 0)
    return render(request, 'accident_app/nearby_services.html', {
        'report':              report,
        'lat':                 lat,
        'lon':                 lon,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    })


# ──────────────────────────────────────────────
# INSURANCE
# ──────────────────────────────────────────────

@login_required
def check_insurance(request):
    result = None
    vehicle_number = ''
    if request.method == 'POST':
        vehicle_number = request.POST.get('vehicle_number', '').strip().upper()
        try:
            result = VehicleInsurance.objects.get(vehicle_number__iexact=vehicle_number)
        except VehicleInsurance.DoesNotExist:
            messages.warning(request, f'No insurance record found for vehicle: {vehicle_number}')
    return render(request, 'accident_app/check_insurance.html', {
        'result': result, 'vehicle_number': vehicle_number
    })


@login_required
def manage_insurance(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    records = VehicleInsurance.objects.all().order_by('vehicle_number')
    return render(request, 'accident_app/manage_insurance.html', {'records': records})


@login_required
def add_insurance(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = InsuranceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Insurance record added successfully!')
        return redirect('manage_insurance')
    return render(request, 'accident_app/add_insurance.html', {'form': form})
