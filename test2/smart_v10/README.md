# Smart Accident Management and Emergency Response System

---

## ✨ Features Added / Updated

### 🔐 SMS OTP Login (Twilio)
- Every login sends a 6-digit OTP to the **mobile number** entered at registration
- OTP auto-submits when 6 digits are typed
- Resend button available; OTP expires in 10 minutes; 3 wrong attempts = lockout

### 📋 Registration Change
- **Mobile number is now required** at registration (was optional before)
- Email also required
- The 10-digit number is validated (must start with 6–9, Indian format)

### 📱 Emergency SMS Alerts
- Emergency alerts go to contacts via both email AND SMS

---

## 🚀 Quick Setup

### Step 1 — Install packages
```
pip install -r requirements.txt
```

### Step 2 — Configure Twilio (for OTP + SMS alerts)

Sign up free at **https://www.twilio.com/try-twilio**, then open `settings.py`:

```python
TWILIO_ACCOUNT_SID  = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'   # Console → Account Info
TWILIO_AUTH_TOKEN   = 'your_auth_token'                      # Console → Account Info
TWILIO_PHONE_NUMBER = '+1xxxxxxxxxx'                         # Console → Phone Numbers
TWILIO_SMS_ENABLED  = True                                   # ← flip this to True
```

> **Free trial note:** Twilio free trial can only send SMS to verified numbers.
> Go to Console → Verified Caller IDs and add the numbers you want to test with.

### Step 3 — Configure Email (for emergency email alerts to contacts)
```python
EMAIL_HOST_USER     = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'   # Gmail App Password
DEFAULT_FROM_EMAIL  = 'Smart Accident System <your@gmail.com>'
```
> Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords

### Step 4 — Migrate and run
```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🔄 Login Flow

```
User enters username + password
        ↓
Credentials verified by Django
        ↓
OTP generated → sent via Twilio SMS to registered mobile number
        ↓
User lands on /login/verify-otp/
        ↓
User enters 6-digit OTP (auto-submits on 6th digit)
        ↓
OTP correct + not expired → logged in ✅
OTP wrong × 3            → locked out, must re-login
OTP expired              → must re-login for a fresh OTP
```

---

## 📂 Changed Files

| File | What changed |
|---|---|
| `forms.py` | `phone_number` now required + validated; `OTPVerificationForm` kept |
| `views.py` | Login sends SMS OTP; register auto-logins (no OTP on first signup); DB lock fix |
| `utils.py` | `send_otp_sms()`, `mask_phone()`, `normalize_to_e164()` added |
| `settings.py` | Twilio config block; SQLite `timeout: 20` to prevent lock errors |
| `templates/register.html` | Phone field highlighted with "OTP sent here" badge |
| `templates/login.html` | Notice updated to say SMS |
| `templates/verify_otp.html` | Shows masked phone number instead of email |

