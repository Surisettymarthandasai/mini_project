from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import Faculty, Student, Subject
from .forms import AdminUserCreationForm, UserRegistrationForm
from .models import Profile


def home(request):
    """Landing page for the application."""
    return render(request, 'users/home.html')


def login_view(request):
    """Custom login view with approval check."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to get the user
        try:
            user = User.objects.get(username=username)
            
            # Check if password is correct
            if user.check_password(password):
                # Check if user has profile and is approved
                try:
                    if not user.profile.is_approved:
                        messages.warning(request, 'Your account is pending admin approval. Please wait for approval before logging in.')
                        return render(request, 'users/login.html')
                except Profile.DoesNotExist:
                    pass  # Superuser without profile
                
                # Check if user is active
                if not user.is_active:
                    messages.error(request, 'Your account has been deactivated. Please contact the administrator.')
                    return render(request, 'users/login.html')
                
                # Authenticate and login
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('dashboard:home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password. Please try again.')
        
        return render(request, 'users/login.html')
    
    return render(request, 'users/login.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User inactive until admin approves
            user.save()
            role = form.cleaned_data.get('role')
            # Use get_or_create to avoid duplicate errors from signals
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'role': role, 'is_approved': False}
            )
            if not created:
                # Update existing profile
                profile.role = role
                profile.is_approved = False
                profile.save()
            messages.success(request, 'Registration submitted! Your account is pending admin approval.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def is_admin(user):
    """Check if user is admin."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.profile.role == Profile.Roles.ADMIN
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(is_admin)
def pending_users(request):
    """View pending user registrations."""
    pending = Profile.objects.filter(is_approved=False).select_related('user').order_by('-created_at')
    return render(request, 'users/pending_users.html', {'pending_users': pending})


@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    """Approve a pending user."""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    profile.is_approved = True
    profile.save()
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved!')
    return redirect('users:pending_users')


@login_required
@user_passes_test(is_admin)
def reject_user(request, user_id):
    """Reject and delete a pending user."""
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()  # This will cascade delete the profile
    messages.warning(request, f'User {username} has been rejected and deleted.')
    return redirect('users:pending_users')


@login_required
@user_passes_test(is_admin)
def create_user(request):
    """Admin manually creates a user with role-specific details."""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Admin-created users are active immediately
            user.save()
            
            role = form.cleaned_data.get('role')
            
            # Use get_or_create to avoid duplicate errors from signals
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'role': role, 'is_approved': True}
            )
            if not created:
                # Update existing profile
                profile.role = role
                profile.is_approved = True
                profile.save()
            
            # Handle Faculty-specific data
            if role == Profile.Roles.FACULTY:
                department = form.cleaned_data.get('department')
                subjects = form.cleaned_data.get('subjects')
                
                if department:
                    # Create or update Faculty profile
                    employee_number = f"FAC{user.id:05d}"
                    faculty, fac_created = Faculty.objects.get_or_create(
                        user=user,
                        defaults={
                            'employee_number': employee_number,
                            'department': department
                        }
                    )
                    if not fac_created:
                        faculty.department = department
                        faculty.save()
                    
                    # Assign subjects
                    if subjects:
                        for subject in subjects:
                            subject.faculty = faculty
                            subject.save()
                        messages.success(
                            request,
                            f'Faculty {user.username} created with {subjects.count()} subject(s)!'
                        )
                    else:
                        messages.success(request, f'Faculty {user.username} created!')
                else:
                    messages.warning(request, f'User {user.username} created but department not set!')
            
            # Handle Student-specific data
            elif role == Profile.Roles.STUDENT:
                batch = form.cleaned_data.get('batch')
                semester = form.cleaned_data.get('semester')
                section = form.cleaned_data.get('section', '')
                
                if batch and semester:
                    registration_number = f"STU{user.id:05d}"
                    student, stu_created = Student.objects.get_or_create(
                        user=user,
                        defaults={
                            'registration_number': registration_number,
                            'batch': batch,
                            'semester': semester,
                            'section': section
                        }
                    )
                    if not stu_created:
                        student.batch = batch
                        student.semester = semester
                        student.section = section
                        student.save()
                    messages.success(request, f'Student {user.username} created!')
                else:
                    messages.warning(request, f'User {user.username} created but student details incomplete!')
            else:
                messages.success(request, f'User {user.username} created successfully!')
            
            return redirect('users:pending_users')
    else:
        form = AdminUserCreationForm()
    return render(request, 'users/create_user.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def get_subjects_by_department(request, department):
    """AJAX endpoint to get subjects filtered by department."""
    # Get all subjects for the department and common subjects (empty department)
    subjects = Subject.objects.filter(
        department__in=[department, '']
    ).values('id', 'code', 'name', 'semester', 'credits').order_by('semester', 'code')
    
    return JsonResponse({
        'subjects': list(subjects)
    })
