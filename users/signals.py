from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from academics.models import Faculty, Student
from users.models import Profile


@receiver(post_save, sender=Profile)
def create_academic_profile(sender, instance, created, **kwargs):
    """
    Automatically create Faculty or Student profile when a user is approved.
    """
    # Only proceed if user is approved and active
    if not instance.is_approved or not instance.user.is_active:
        return
    
    # Create Faculty profile if role is FACULTY and doesn't exist
    if instance.role == Profile.Roles.FACULTY:
        if not hasattr(instance.user, 'faculty_profile'):
            # Generate employee number if not exists
            employee_number = f"FAC{instance.user.id:05d}"
            Faculty.objects.get_or_create(
                user=instance.user,
                defaults={
                    'employee_number': employee_number,
                    'department': Faculty.Department.CSE  # Default department
                }
            )
    
    # Create Student profile if role is STUDENT
    elif instance.role == Profile.Roles.STUDENT:
        if not hasattr(instance.user, 'student_profile'):
            # Generate registration number if not exists
            registration_number = f"STU{instance.user.id:05d}"
            Student.objects.get_or_create(
                user=instance.user,
                defaults={
                    'registration_number': registration_number,
                    'batch': '2026',  # Default batch
                    'semester': 1,  # Default semester
                    'section': 'A'  # Default section
                }
            )


@receiver(post_save, sender=User)
def create_profile_signal(sender, instance, created, **kwargs):
    """
    Ensure every user has a profile.
    This is a fallback in case profile isn't created during registration.
    """
    if created:
        # Don't create profile for superuser
        if not instance.is_superuser:
            # Use get_or_create to avoid duplicate errors
            Profile.objects.get_or_create(user=instance)
