"""
Management command to manage users without losing their data.

Usage:
  python manage.py manage_users --list
      → List all users and their report counts

  python manage.py manage_users --reset-password USERNAME NEWPASSWORD
      → Reset a user's password (all reports/data kept safe)

  python manage.py manage_users --create USERNAME PASSWORD EMAIL
      → Create a new user (or update password if already exists)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accident_app.models import AccidentReport, UserProfile


class Command(BaseCommand):
    help = 'Manage users — list, reset passwords, create users (data is always preserved)'

    def add_arguments(self, parser):
        parser.add_argument('--list',   action='store_true', help='List all users')
        parser.add_argument('--reset-password', nargs=2, metavar=('USERNAME', 'NEWPASSWORD'),
                            help='Reset a user password')
        parser.add_argument('--create', nargs=3, metavar=('USERNAME', 'PASSWORD', 'EMAIL'),
                            help='Create user or update password if exists')

    def handle(self, *args, **options):
        if options['list']:
            self._list_users()
        elif options['reset_password']:
            self._reset_password(*options['reset_password'])
        elif options['create']:
            self._create_user(*options['create'])
        else:
            self.stdout.write(self.style.WARNING(
                'Usage:\n'
                '  python manage.py manage_users --list\n'
                '  python manage.py manage_users --reset-password USERNAME NEWPASSWORD\n'
                '  python manage.py manage_users --create USERNAME PASSWORD EMAIL\n'
            ))

    def _list_users(self):
        users = User.objects.all().order_by('date_joined')
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found.'))
            return
        self.stdout.write(self.style.SUCCESS(f'\n{"─"*60}'))
        self.stdout.write(f'{"USERNAME":<20} {"EMAIL":<30} {"REPORTS":>7}')
        self.stdout.write(f'{"─"*60}')
        for u in users:
            count = AccidentReport.objects.filter(user=u).count()
            self.stdout.write(f'{u.username:<20} {u.email:<30} {count:>7}')
        self.stdout.write(f'{"─"*60}\n')

    def _reset_password(self, username, new_password):
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            count = AccidentReport.objects.filter(user=user).count()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Password reset for "{username}". '
                f'All {count} report(s) and data preserved.'
            ))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'❌ User "{username}" not found. '
                f'Run --list to see all users.'
            ))

    def _create_user(self, username, password, email):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.email = email
        user.save()
        UserProfile.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ User "{username}" created successfully.'))
        else:
            count = AccidentReport.objects.filter(user=user).count()
            self.stdout.write(self.style.SUCCESS(
                f'✅ Password updated for existing user "{username}". '
                f'{count} report(s) preserved.'
            ))
