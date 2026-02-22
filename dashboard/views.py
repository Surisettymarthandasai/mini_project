from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import render, redirect
from django.utils import timezone

from academics.models import Assignment, Attendance, Faculty, Marks, Student, Subject, Submission
from users.models import Profile


@login_required
def home(request):
	"""Route to role-specific dashboard."""
	role = None
	try:
		profile = request.user.profile
		role = profile.role
		# Check if user is approved (or is admin/superuser)
		if not profile.is_approved and not request.user.is_superuser and profile.role != Profile.Roles.ADMIN:
			return render(request, 'users/pending_approval.html')
	except Profile.DoesNotExist:
		if request.user.is_superuser:
			role = Profile.Roles.ADMIN
		else:
			return redirect('users:login')

	# Route to role-specific dashboard
	if role == Profile.Roles.STUDENT:
		return student_dashboard(request)
	elif role == Profile.Roles.FACULTY:
		return faculty_dashboard(request)
	elif role == Profile.Roles.ADMIN:
		return admin_dashboard(request)
	else:
		return redirect('users:login')


@login_required
def student_dashboard(request):
	"""Dashboard for students showing their academic information."""
	try:
		student = request.user.student_profile
	except Student.DoesNotExist:
		return render(request, 'dashboard/no_profile.html', {
			'message': 'Student profile not found. Please contact administrator.'
		})
	
	# Get student's attendance records
	attendance_records = Attendance.objects.filter(student=student).select_related('subject', 'faculty')
	
	# Calculate attendance percentage by subject
	attendance_by_subject = {}
	for record in attendance_records:
		subject_code = record.subject.code
		if subject_code not in attendance_by_subject:
			attendance_by_subject[subject_code] = {
				'subject': record.subject,
				'total': 0,
				'present': 0
			}
		attendance_by_subject[subject_code]['total'] += 1
		if record.status == Attendance.Status.PRESENT:
			attendance_by_subject[subject_code]['present'] += 1
	
	# Calculate percentage
	for data in attendance_by_subject.values():
		data['percentage'] = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
	
	# Get student's marks
	marks = Marks.objects.filter(student=student).select_related('subject').order_by('-recorded_at')[:10]
	
	# Get enrolled subjects (subjects with attendance or marks)
	enrolled_subject_ids = set(attendance_records.values_list('subject_id', flat=True)) | set(marks.values_list('subject_id', flat=True))
	enrolled_subjects = Subject.objects.filter(id__in=enrolled_subject_ids).select_related('faculty')
	
	# Get assignments
	assignments = Assignment.objects.filter(
		subject__in=enrolled_subjects
	).select_related('subject', 'faculty').order_by('-due_date')[:10]
	
	# Get submissions
	submissions = Submission.objects.filter(
		student=student
	).select_related('assignment__subject').order_by('-submitted_on')[:5]
	
	stats = {
		'total_subjects': enrolled_subjects.count(),
		'total_attendance': attendance_records.count(),
		'present_count': attendance_records.filter(status=Attendance.Status.PRESENT).count(),
		'assignments': Assignment.objects.filter(subject__in=enrolled_subjects).count(),
		'submissions': submissions.count(),
		'average_marks': marks.aggregate(Avg('score'))['score__avg'] or 0,
	}
	
	# Calculate overall attendance percentage
	if stats['total_attendance'] > 0:
		stats['attendance_percentage'] = (stats['present_count'] / stats['total_attendance']) * 100
	else:
		stats['attendance_percentage'] = 0
	
	return render(request, 'dashboard/student_dashboard.html', {
		'student': student,
		'stats': stats,
		'attendance_by_subject': attendance_by_subject,
		'recent_marks': marks,
		'enrolled_subjects': enrolled_subjects,
		'assignments': assignments,
		'submissions': submissions,
		'today': timezone.now().date(),
	})


@login_required
def faculty_dashboard(request):
	"""Dashboard for faculty showing their teaching information."""
	try:
		faculty = request.user.faculty_profile
	except Faculty.DoesNotExist:
		return render(request, 'dashboard/no_profile.html', {
			'message': 'Faculty profile not found. Please contact administrator.'
		})
	
	# Get subjects taught by this faculty
	subjects = faculty.subjects.all()
	
	# Get students enrolled in faculty's subjects
	students_enrolled = Student.objects.filter(
		attendance_records__subject__in=subjects
	).distinct()
	
	# Get attendance records taken by this faculty
	attendance_records = Attendance.objects.filter(faculty=faculty).select_related('student', 'subject')
	
	# Get assignments created by this faculty
	assignments = faculty.assignments.all().select_related('subject').order_by('-created_at')[:10]
	
	# Get recent marks entered
	marks = Marks.objects.filter(subject__in=subjects).select_related('student', 'subject').order_by('-recorded_at')[:10]
	
	# Statistics
	# Note: use assignment_ids (list) to avoid MySQL LIMIT-in-subquery error
	assignment_ids = list(faculty.assignments.values_list('id', flat=True))
	stats = {
		'subjects_teaching': subjects.count(),
		'total_students': students_enrolled.count(),
		'attendance_records': attendance_records.count(),
		'assignments_created': faculty.assignments.count(),
		'marks_entered': Marks.objects.filter(subject__in=subjects).count(),
		'pending_submissions': Submission.objects.filter(
			assignment_id__in=assignment_ids,
			status=Submission.SubmissionStatus.SUBMITTED
		).count(),
	}
	
	# Attendance by subject
	attendance_by_subject = {}
	for subject in subjects:
		total = Attendance.objects.filter(subject=subject, faculty=faculty).count()
		present = Attendance.objects.filter(
			subject=subject,
			faculty=faculty,
			status=Attendance.Status.PRESENT
		).count()
		if total > 0:
			attendance_by_subject[subject.code] = {
				'subject': subject,
				'total': total,
				'present': present,
				'percentage': (present / total * 100)
			}
	
	# Get recent attendance records taken by this faculty
	recent_attendance = Attendance.objects.filter(faculty=faculty).select_related('student', 'subject').order_by('-created_at')[:10]
	
	return render(request, 'dashboard/faculty_dashboard.html', {
		'faculty': faculty,
		'stats': stats,
		'subjects': subjects,
		'students_enrolled': students_enrolled[:10],
		'attendance_by_subject': attendance_by_subject,
		'recent_assignments': assignments,
		'recent_marks': marks,
		'recent_attendance': recent_attendance,
	})


@login_required
def admin_dashboard(request):
	"""Dashboard for admin showing overall system statistics."""
	stats = {
		"students": Student.objects.count(),
		"faculty": Faculty.objects.count(),
		"subjects": Subject.objects.count(),
		"assignments": Assignment.objects.count(),
		"attendance": Attendance.objects.count(),
		"marks": Marks.objects.count(),
		"pending_users": Profile.objects.filter(is_approved=False).count(),
	}
	
	# Get ALL students and faculty for real-time display
	all_students = Student.objects.all().select_related('user').order_by('-created_at')
	all_faculty = Faculty.objects.all().select_related('user').order_by('-created_at')
	
	# Recent activities (keep for backwards compatibility)
	recent_students = Student.objects.all().select_related('user').order_by('-created_at')[:5]
	recent_faculty = Faculty.objects.all().select_related('user').order_by('-created_at')[:5]
	pending_users = Profile.objects.filter(is_approved=False).select_related('user').order_by('-created_at')[:10]
	
	# All users for real-time display
	all_users = Profile.objects.all().select_related('user').order_by('-created_at')
	
	# Subject-wise statistics
	subject_stats = Subject.objects.annotate(
		student_count=Count('attendance_records__student', distinct=True),
		attendance_count=Count('attendance_records')
	).order_by('-student_count')[:10]

	return render(
		request,
		"dashboard/admin_dashboard.html",
		{
			"role": Profile.Roles.ADMIN,
			"user": request.user,
			"stats": stats,
			"recent_students": recent_students,
			"recent_faculty": recent_faculty,
			"all_students": all_students,
			"all_faculty": all_faculty,
			"pending_users": pending_users,
			"all_users": all_users,
			"subject_stats": subject_stats,
		},
	)
