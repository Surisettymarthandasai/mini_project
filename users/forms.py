from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    role = forms.ChoiceField(
        choices=[(r, r) for r in ['STUDENT', 'FACULTY']],  # Exclude ADMIN from public registration
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class AdminUserCreationForm(UserCreationForm):
    """Form for admin to manually create users."""
    from academics.models import Faculty, Subject
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    role = forms.ChoiceField(choices=Profile.Roles.choices, required=True)
    
    # Faculty-specific fields
    department = forms.ChoiceField(
        choices=[('', '-- Select Department --')] + list(Faculty.Department.choices),
        required=False,
        help_text="Required for Faculty role"
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select subjects to assign (for Faculty)"
    )
    
    # Student-specific fields
    batch = forms.CharField(max_length=32, required=False, help_text="Required for Student role")
    semester = forms.IntegerField(
        min_value=1,
        max_value=8,
        required=False,
        help_text="Required for Student role"
    )
    section = forms.CharField(max_length=8, required=False, help_text="Optional for Student")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                continue
            field.widget.attrs.setdefault('class', 'form-control')


class FacultySubjectAssignmentForm(forms.Form):
    """Form for assigning subjects to faculty during approval."""
    from academics.models import Faculty, Subject
    
    department = forms.ChoiceField(
        choices=Faculty.Department.choices,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select subjects to assign to this faculty"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will be filtered by AJAX based on department selection
