import re
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmergencyContact, VehicleInsurance, AccidentReport


def validate_indian_phone(value):
    """Accept 10-digit Indian numbers, optionally prefixed with +91 or 0."""
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    if cleaned.startswith('+91'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]
    if not re.fullmatch(r'[6-9]\d{9}', cleaned):
        raise forms.ValidationError(
            'Enter a valid 10-digit Indian mobile number (e.g. 9876543210).'
        )


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone_number = forms.CharField(
        max_length=15, required=True,
        validators=[validate_indian_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number (e.g. 9876543210)',
            'inputmode': 'numeric',
        }),
        help_text='OTP will be sent to this number every time you log in.')
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone_number(self):
        """Normalize to plain 10-digit string."""
        value = self.cleaned_data.get('phone_number', '')
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        if cleaned.startswith('+91'):
            cleaned = cleaned[3:]
        elif cleaned.startswith('91') and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith('0'):
            cleaned = cleaned[1:]
        return cleaned  # store as plain 10 digits, e.g. "9876543210"


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True,
        }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }))


class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Enter OTP',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center otp-input',
            'placeholder': '• • • • • •',
            'maxlength': '6',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'autofocus': True,
        })
    )

    def clean_otp_code(self):
        otp = self.cleaned_data.get('otp_code', '').strip()
        if not otp.isdigit():
            raise forms.ValidationError('OTP must be 6 digits only.')
        return otp


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Father, Mother, Spouse'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (e.g. 9876543210)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }
        help_texts = {
            'phone': 'Enter 10-digit number without country code.',
        }


class AccidentReportForm(forms.ModelForm):
    class Meta:
        model = AccidentReport
        fields = ['image', 'vehicle_number', 'latitude', 'longitude', 'location_address', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Number (optional)'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'location_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location (auto-detected or enter manually)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes about the accident...'}),
        }


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = VehicleInsurance
        fields = '__all__'
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_company': forms.TextInput(attrs={'class': 'form-control'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'coverage_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
        }
