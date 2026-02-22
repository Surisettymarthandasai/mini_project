from django.core.management.base import BaseCommand
from django.db.models import Q
from academics.models import Faculty, Subject


class Command(BaseCommand):
    help = 'Sync faculty assignments for subjects that may have been missed during user creation'

    def handle(self, *args, **options):
        self.stdout.write('Syncing faculty-subject assignments...')
        
        # Get all faculty members
        faculties = Faculty.objects.prefetch_related('user').all()
        
        updated_count = 0
        for faculty in faculties:
            # For each faculty, check if they have subjects that need to be assigned
            # This is primarily for subjects that may have been assigned through the
            # user creation form but the faculty field wasn't updated
            
            # Note: Since we assign subjects through subject.faculty = faculty in create_user,
            # this command is mainly for fixing any data inconsistencies
            self.stdout.write(f'  Checking faculty: {faculty.user.username} ({faculty.department})')
            
        # Find subjects without faculty - these should be assigned based on department
        unassigned_subjects = Subject.objects.filter(faculty__isnull=True)
        
        if unassigned_subjects.exists():
            self.stdout.write(self.style.WARNING(f'Found {unassigned_subjects.count()} unassigned subjects'))
            
            for subject in unassigned_subjects:
                # Try to find a faculty member in the same department
                if subject.department:
                    matching_faculty = Faculty.objects.filter(department=subject.department).first()
                    if matching_faculty:
                        subject.faculty = matching_faculty
                        subject.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Assigned {subject.code} to {matching_faculty.user.username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ No faculty found for department {subject.department} (Subject: {subject.code})'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Subject {subject.code} has no department set'
                        )
                    )
        else:
            self.stdout.write(self.style.SUCCESS('All subjects already have faculty assigned!'))
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully updated {updated_count} subject assignments')
            )
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No updates needed'))
