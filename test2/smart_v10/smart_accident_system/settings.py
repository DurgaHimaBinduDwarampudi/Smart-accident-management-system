from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-smart-accident-mgmt-key-change-in-production-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accident_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_accident_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_accident_system.wsgi.application'

# ── Database ─────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,   # Wait up to 20s if database is locked
        },
        'CONN_MAX_AGE': 0,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ── Session & Cookie persistence ─────────────
# Sessions persist for 30 days — users stay logged in across restarts
SESSION_ENGINE           = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE       = 60 * 60 * 24 * 30   # 30 days in seconds
SESSION_SAVE_EVERY_REQUEST = True               # Refresh expiry on every request
SESSION_COOKIE_HTTPONLY  = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False         # Don't expire when browser closes

# ── Email Configuration ───────────────────────
# ── Email Configuration ───────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'himabindu1452004@gmail.com'
EMAIL_HOST_PASSWORD = 'ecss meqs gcfy mend'
DEFAULT_FROM_EMAIL  = 'Smart Accident System <himabindu1452004@gmail.com>'

# ── Twilio SMS Configuration ─────────────────
# OTP login verification and emergency SMS alerts both use Twilio.
# Sign up FREE at https://www.twilio.com/try-twilio
# Steps:
#   1. Create account → get Account SID + Auth Token from Console dashboard
#   2. Get a Twilio phone number (free trial gives you one)
#   3. Fill in the three values below and set TWILIO_SMS_ENABLED = True
TWILIO_ACCOUNT_SID  = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # ← Your Account SID
TWILIO_AUTH_TOKEN   = 'your_auth_token_here'               # ← Your Auth Token
TWILIO_PHONE_NUMBER = '+1xxxxxxxxxx'                       # ← Your Twilio number (E.164 format)
TWILIO_SMS_ENABLED  = False  # ← Set to True after filling the three values above

# ── Hugging Face API Key (FREE — for vehicle damage analysis) ────────────────
# Get your FREE key at https://huggingface.co/settings/tokens
# Steps:
#   1. Sign up free at https://huggingface.co
#   2. Go to Settings → Access Tokens → New Token
#   3. Select "Read" role → Create → copy the token (starts with hf_...)
#   4. Paste it below — free tier gives ~300-500 requests/day per model
HUGGINGFACE_API_KEY = 'YOUR_HUGGINGFACE_API_KEY'  # ← Paste your hf_... token here

# ── Google Maps API Key ───────────────────────
# Required for live hospital + mechanic shop search on the Nearby Services page.
#
# How to get your key (free tier is enough):
#   1. Go to https://console.cloud.google.com/
#   2. Create a project → Enable "Maps JavaScript API" + "Places API"
#   3. APIs & Services → Credentials → Create API Key
#   4. (Recommended) Restrict the key to your domain under "API restrictions"
#   5. Paste it below:
#
GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'  # ← Paste your key here
#
# Without a key the page falls back to OpenStreetMap/Overpass API which has
# sparse coverage in rural India and may show 0 results.

# ── OTP Settings ─────────────────────────────
OTP_EXPIRY_MINUTES = 10   # How long the OTP stays valid
OTP_MAX_ATTEMPTS   = 3    # Wrong attempts before user must re-login
