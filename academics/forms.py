from django import forms

from .models import Assignment, Attendance, Faculty, Marks, Submission


class _StyledModelForm(forms.ModelForm):
    """Applies Bootstrap form-control to widgets for consistency."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.setdefault("class", "form-control")


class AttendanceForm(_StyledModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "subject", "date", "status"]


class MarksForm(_StyledModelForm):
    class Meta:
        model = Marks
        fields = ["student", "subject", "assessment_type", "score", "max_score"]


class AssignmentForm(_StyledModelForm):
    class Meta:
        model = Assignment
        fields = ["subject", "title", "description", "due_date", "max_score"]


class SubmissionForm(_StyledModelForm):
    class Meta:
        model = Submission
        fields = ["assignment", "student", "submitted_on", "status", "score", "remarks"]


class SubjectFacultyAssignmentForm(forms.Form):
    """Form for assigning faculty to a subject."""
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select faculty to assign to this subject"
    )

    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', None)
        super().__init__(*args, **kwargs)
        if subject and subject.department:
            # Filter faculty by department
            self.fields['faculty'].queryset = Faculty.objects.filter(department=subject.department)
        
        # Customize the display to show name, employee number, and department
        self.fields['faculty'].label_from_instance = lambda obj: f"{obj.user.get_full_name() or obj.user.username} ({obj.employee_number}) - {obj.get_department_display()}"
