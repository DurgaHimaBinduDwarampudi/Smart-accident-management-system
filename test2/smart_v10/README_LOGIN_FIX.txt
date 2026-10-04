━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMART ACCIDENT SYSTEM — LOGIN FIX GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY LOGIN WAS FAILING
─────────────────────
The old system required an OTP (one-time password) sent via
email/SMS to complete login. If the OTP email failed to send
(wrong Gmail password, Gmail blocking it, etc.) the user
was stuck on the OTP page and thought their password was wrong.

WHAT IS FIXED NOW
─────────────────
✅ Login now works with just username + password.
   OTP is OPTIONAL — if it can't be sent, you are still
   logged in directly (your password was already verified).

✅ Sessions last 30 days — you stay logged in across
   browser restarts and server restarts.

✅ Your accident reports, profile and data are ALWAYS
   saved in db.sqlite3 — they never disappear on restart.


HOW TO RECOVER YOUR EXISTING ACCOUNT
──────────────────────────────────────
If you can't remember your password, run this command
from the project folder:

  # See all users and their report counts:
  python manage.py manage_users --list

  # Reset your password (keeps all your reports safe):
  python manage.py manage_users --reset-password valli newpassword123

  # Create a new user (or update password if already exists):
  python manage.py manage_users --create valli newpassword123 email@example.com


HOW TO KEEP YOUR DATA SAFE
───────────────────────────
Your data lives in:  db.sqlite3  (in the project root folder)
Your images live in: media/accidents/  and  media/profiles/

IMPORTANT: When you copy or move the project to another
computer, also copy:
  ✅ db.sqlite3
  ✅ media/ folder

Without these two, your reports and user accounts will be gone.


QUICK START (fresh install on a new machine)
─────────────────────────────────────────────
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py manage_users --create admin admin123 admin@example.com
  python manage.py runserver

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
