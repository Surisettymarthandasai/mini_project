from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile


class Command(BaseCommand):
    help = 'Clean up data inconsistencies'

    def handle(self, *args, **kwargs):
        """Clean up inconsistent data."""
        
        # Delete fact123 user with wrong data
        user5 = User.objects.filter(id=5).first()
        if user5:
            user5.delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted fact123'))
        
        # Create profile for anand123
        user3 = User.objects.filter(id=3).first()
        if user3 and not hasattr(user3, 'profile'):
            Profile.objects.create(user=user3, role='FACULTY', is_approved=True)
            self.stdout.write(self.style.SUCCESS('✓ Created profile for anand123'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Cleanup complete!'))
