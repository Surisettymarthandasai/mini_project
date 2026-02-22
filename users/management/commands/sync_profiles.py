from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from academics.models import Faculty, Student
from users.models import Profile


class Command(BaseCommand):
    help = 'Synchronize User/Profile with Faculty/Student profiles'

    def handle(self, *args, **kwargs):
        """Sync existing users with academic profiles."""
        synced_faculty = 0
        synced_students = 0
        
        self.stdout.write("Starting synchronization...\n")
        
        # Get all approved users
        profiles = Profile.objects.filter(is_approved=True).select_related('user')
        
        for profile in profiles:
            user = profile.user
            
            # Sync Faculty
            if profile.role == Profile.Roles.FACULTY:
                if not hasattr(user, 'faculty_profile'):
                    employee_number = f"FAC{user.id:05d}"
                    Faculty.objects.create(
                        user=user,
                        employee_number=employee_number,
                        department=Faculty.Department.CSE  # Default to CSE
                    )
                    synced_faculty += 1
                    self.stdout.write(f"  ✓ Created Faculty profile for {user.username}")
            
            # Sync Student  
            elif profile.role == Profile.Roles.STUDENT:
                if not hasattr(user, 'student_profile'):
                    registration_number = f"STU{user.id:05d}"
                    Student.objects.create(
                        user=user,
                        registration_number=registration_number,
                        batch='2026',
                        semester=1
                    )
                    synced_students += 1
                    self.stdout.write(f"  ✓ Created Student profile for {user.username}")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Synchronization complete!\n"
            f"  Faculty profiles created: {synced_faculty}\n"
            f"  Student profiles created: {synced_students}"
        ))
