"""
Management command to clear all active sessions.
Useful for forcing logout of all users (e.g., on server restart).
"""
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clear all active sessions - forces all users to logout'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all sessions including expired ones',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Delete all sessions
            count = Session.objects.all().count()
            Session.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleared all {count} sessions')
            )
        else:
            # Delete only non-expired sessions (active users)
            from django.utils import timezone
            count = Session.objects.filter(expire_date__gte=timezone.now()).count()
            Session.objects.filter(expire_date__gte=timezone.now()).delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleared {count} active sessions')
            )
        
        self.stdout.write('')
        self.stdout.write('All users have been logged out.')
        self.stdout.write('They will need to login again.')
