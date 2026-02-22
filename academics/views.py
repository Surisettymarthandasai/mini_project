from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.models import Profile

from .forms import AssignmentForm, AttendanceForm, MarksForm, SubmissionForm, SubjectFacultyAssignmentForm
from .models import Assignment, Attendance, Marks, Student, Subject, Submission


@login_required
def subject_list(request):
    subjects = Subject.objects.select_related("faculty__user").all()
    return render(request, "academics/subject_list.html", {
        "subjects": subjects,
        "user_role": _get_user_role(request.user)
    })


@login_required
def attendance_summary(request):
    summary = (
        Attendance.objects.select_related("subject")
        .values("subject__code", "subject__name")
        .order_by("subject__code")
    )
    total_by_subject = {}
    for record in summary:
        key = f"{record['subject__code']} - {record['subject__name']}"
        total_by_subject.setdefault(key, {"present": 0, "absent": 0})

    queryset = Attendance.objects.select_related("subject", "student")
    user_role = _get_user_role(request.user)
    if user_role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            queryset = queryset.filter(student=student_profile)
    for att in queryset:
        key = f"{att.subject.code} - {att.subject.name}"
        if att.status == Attendance.Status.PRESENT:
            total_by_subject[key]["present"] += 1
        else:
            total_by_subject[key]["absent"] += 1
    
    # Calculate percentages by student
    student_percentages = {}
    if user_role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            students = [student_profile]
        else:
            students = []
    else:
        students = Student.objects.all()
    
    for student in students:
        student_records = Attendance.objects.filter(student=student)
        total = student_records.count()
        if total > 0:
            present_count = student_records.filter(status=Attendance.Status.PRESENT).count()
            percentage = (present_count / total) * 100
            student_percentages[student] = {
                "total": total,
                "present": present_count,
                "percentage": round(percentage, 2)
            }
    
    return render(
        request,
        "academics/attendance_summary.html",
        {"summary": total_by_subject, "student_percentages": student_percentages},
    )


@login_required
def marks_overview(request):
    marks = Marks.objects.select_related("student", "subject")
    user_role = _get_user_role(request.user)
    if user_role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            marks = marks.filter(student=student_profile)
    elif user_role == Profile.Roles.FACULTY:
        faculty_profile = getattr(request.user, "faculty_profile", None)
        if faculty_profile:
            marks = marks.filter(subject__faculty=faculty_profile)
    return render(request, "academics/marks_overview.html", {"marks": marks})


def _get_faculty_for_user(user):
    """Best-effort lookup of faculty profile from authenticated user."""
    return getattr(user, "faculty_profile", None)


def _get_user_role(user):
    try:
        return user.profile.role
    except Profile.DoesNotExist:
        if user.is_superuser:
            return Profile.Roles.ADMIN
    return None


@login_required
def attendance_create(request):
    faculty = _get_faculty_for_user(request.user)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can record attendance.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.faculty = faculty
            attendance.save()
            messages.success(request, "Attendance recorded.")
            return redirect("academics:attendance_list")
    else:
        form = AttendanceForm()
    return render(request, "academics/attendance_form.html", {"form": form})


@login_required
def marks_create(request):
    faculty = _get_faculty_for_user(request.user)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can record marks.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = MarksForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Marks recorded.")
            return redirect("academics:marks_overview")
    else:
        form = MarksForm()
    return render(request, "academics/marks_form.html", {"form": form})


@login_required
def assignment_create(request):
    faculty = _get_faculty_for_user(request.user)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can create assignments.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.faculty = faculty
            assignment.save()
            messages.success(request, "Assignment created.")
            return redirect("academics:assignment_list")
    else:
        form = AssignmentForm()
    return render(request, "academics/assignment_form.html", {"form": form})


@login_required
def submission_create(request):
    if _get_user_role(request.user) not in (Profile.Roles.FACULTY, Profile.Roles.ADMIN):
        messages.error(request, "Only faculty can record submissions.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission recorded.")
            return redirect("academics:submission_list")
    else:
        form = SubmissionForm()
    return render(request, "academics/submission_form.html", {"form": form})


@login_required
def student_submit_assignment(request, assignment_id):
    """Allow students to submit assignments with file upload."""
    from django.utils import timezone
    
    if _get_user_role(request.user) != Profile.Roles.STUDENT:
        messages.error(request, "Only students can submit assignments.")
        return redirect("dashboard:home")
    
    student_profile = getattr(request.user, "student_profile", None)
    if not student_profile:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard:home")
    
    try:
        assignment = Assignment.objects.get(pk=assignment_id)
    except Assignment.DoesNotExist:
        messages.error(request, "Assignment not found.")
        return redirect("academics:assignment_list")
    
    # Check if already submitted
    existing_submission = Submission.objects.filter(
        assignment=assignment,
        student=student_profile
    ).first()
    
    if request.method == "POST":
        if existing_submission:
            messages.warning(request, "You have already submitted this assignment.")
            return redirect("academics:assignment_list")
        
        # Check if file was uploaded
        if 'submission_file' not in request.FILES:
            messages.error(request, "Please upload your assignment file.")
            return render(request, "academics/student_submit_assignment.html", {
                "assignment": assignment,
                "existing_submission": existing_submission,
                "error": "File upload is required"
            })
        
        uploaded_file = request.FILES['submission_file']
        
        # Validate file size (e.g., max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, "File size must be less than 10MB.")
            return render(request, "academics/student_submit_assignment.html", {
                "assignment": assignment,
                "existing_submission": existing_submission,
                "error": "File too large"
            })
        
        # Create submission with file
        submission = Submission.objects.create(
            assignment=assignment,
            student=student_profile,
            submission_file=uploaded_file,
            submitted_on=timezone.now().date(),
            status=Submission.SubmissionStatus.SUBMITTED if timezone.now().date() <= assignment.due_date else Submission.SubmissionStatus.LATE
        )
        
        messages.success(request, f"Assignment '{assignment.title}' submitted successfully with file: {uploaded_file.name}")
        return redirect("academics:assignment_list")
    
    return render(request, "academics/student_submit_assignment.html", {
        "assignment": assignment,
        "existing_submission": existing_submission
    })


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related("subject", "faculty")
    role = _get_user_role(request.user)
    student_profile = None
    
    if role == Profile.Roles.FACULTY:
        faculty_profile = getattr(request.user, "faculty_profile", None)
        if faculty_profile:
            assignments = assignments.filter(faculty=faculty_profile)
    elif role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            assignments = assignments.filter(subject__attendance_records__student=student_profile).distinct()
    
    # For students, annotate each assignment with their submission
    assignments_list = list(assignments)
    if role == Profile.Roles.STUDENT and student_profile:
        submissions = Submission.objects.filter(
            student=student_profile,
            assignment__in=assignments_list
        ).select_related('assignment')
        
        submission_dict = {sub.assignment_id: sub for sub in submissions}
        
        for assignment in assignments_list:
            assignment.student_submission = submission_dict.get(assignment.id)
    
    return render(request, "academics/assignment_list.html", {
        "assignments": assignments_list,
        "user_role": role
    })


@login_required
def attendance_list(request):
    """Detailed attendance list for managing individual records."""
    attendances = Attendance.objects.select_related("student", "subject", "faculty")
    role = _get_user_role(request.user)
    if role == Profile.Roles.FACULTY:
        faculty_profile = getattr(request.user, "faculty_profile", None)
        if faculty_profile:
            attendances = attendances.filter(faculty=faculty_profile)
    elif role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            attendances = attendances.filter(student=student_profile)
    return render(request, "academics/attendance_list.html", {"attendances": attendances})


@login_required
def submission_list(request):
    submissions = Submission.objects.select_related("assignment", "student", "assignment__subject")
    role = _get_user_role(request.user)
    if role == Profile.Roles.FACULTY:
        faculty_profile = getattr(request.user, "faculty_profile", None)
        if faculty_profile:
            submissions = submissions.filter(assignment__faculty=faculty_profile)
    elif role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            submissions = submissions.filter(student=student_profile)
    return render(request, "academics/submission_list.html", {"submissions": submissions})


@login_required
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can edit attendance.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance updated.")
            return redirect("academics:attendance_summary")
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, "academics/attendance_form.html", {"form": form, "edit_mode": True})


@login_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can delete attendance.")
        return redirect("dashboard:home")
    if request.method == "POST":
        attendance.delete()
        messages.success(request, "Attendance deleted.")
        return redirect("academics:attendance_summary")
    return render(request, "academics/attendance_confirm_delete.html", {"attendance": attendance})


@login_required
def marks_edit(request, pk):
    mark = get_object_or_404(Marks, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can edit marks.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = MarksForm(request.POST, instance=mark)
        if form.is_valid():
            form.save()
            messages.success(request, "Marks updated.")
            return redirect("academics:marks_overview")
    else:
        form = MarksForm(instance=mark)
    return render(request, "academics/marks_form.html", {"form": form, "edit_mode": True})


@login_required
def marks_delete(request, pk):
    mark = get_object_or_404(Marks, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can delete marks.")
        return redirect("dashboard:home")
    if request.method == "POST":
        mark.delete()
        messages.success(request, "Marks deleted.")
        return redirect("academics:marks_overview")
    return render(request, "academics/marks_confirm_delete.html", {"mark": mark})


@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can edit assignments.")
        return redirect("dashboard:home")
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("academics:assignment_list")
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, "academics/assignment_form.html", {"form": form, "edit_mode": True})


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if _get_user_role(request.user) != Profile.Roles.FACULTY:
        messages.error(request, "Only faculty can delete assignments.")
        return redirect("dashboard:home")
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("academics:assignment_list")
    return render(request, "academics/assignment_confirm_delete.html", {"assignment": assignment})


@login_required
def subject_assign_faculty(request, pk):
    """View for admin to assign faculty to a subject."""
    if _get_user_role(request.user) != Profile.Roles.ADMIN:
        messages.error(request, "Only admins can assign faculty to subjects.")
        return redirect("dashboard:home")
    
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        form = SubjectFacultyAssignmentForm(request.POST, subject=subject)
        if form.is_valid():
            faculty = form.cleaned_data['faculty']
            subject.faculty = faculty
            subject.save()
            messages.success(request, f"Assigned {faculty.user.get_full_name()} to {subject.name}.")
            return redirect("academics:subject_list")
    else:
        form = SubjectFacultyAssignmentForm(subject=subject)
    
    return render(request, "academics/subject_assign_faculty.html", {
        "form": form,
        "subject": subject
    })


@login_required
def subject_unassign_faculty(request, pk):
    """View for admin to unassign faculty from a subject."""
    if _get_user_role(request.user) != Profile.Roles.ADMIN:
        messages.error(request, "Only admins can unassign faculty from subjects.")
        return redirect("dashboard:home")
    
    subject = Subject.objects.get(pk=pk)
    if subject.faculty:
        faculty_name = subject.faculty.user.get_full_name()
        subject.faculty = None
        subject.save()
        messages.success(request, f"Unassigned {faculty_name} from {subject.name}.")
    else:
        messages.warning(request, f"No faculty was assigned to {subject.name}.")
    
    return redirect("academics:subject_list")


@login_required
def attendance_detailed(request):
    """Detailed attendance view showing individual records with date/time for all roles."""
    user_role = _get_user_role(request.user)
    
    # Base queryset with all related data
    attendances = Attendance.objects.select_related(
        "student__user", "subject", "faculty__user"
    ).order_by("-created_at")
    
    # Filter based on user role
    if user_role == Profile.Roles.STUDENT:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile:
            attendances = attendances.filter(student=student_profile)
        else:
            attendances = Attendance.objects.none()
    elif user_role == Profile.Roles.FACULTY:
        faculty_profile = getattr(request.user, "faculty_profile", None)
        if faculty_profile:
            attendances = attendances.filter(faculty=faculty_profile)
        else:
            attendances = Attendance.objects.none()
    # Admin sees all records
    
    # Group by date for better organization
    attendance_by_date = {}
    for attendance in attendances:
        date_key = attendance.date
        if date_key not in attendance_by_date:
            attendance_by_date[date_key] = []
        attendance_by_date[date_key].append(attendance)
    
    # Sort dates in descending order
    sorted_dates = sorted(attendance_by_date.keys(), reverse=True)
    
    context = {
        "attendance_by_date": attendance_by_date,
        "sorted_dates": sorted_dates,
        "user_role": user_role,
        "total_records": attendances.count(),
    }
    
    return render(request, "academics/attendance_detailed.html", context)
