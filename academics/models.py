from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Student(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
	registration_number = models.CharField(max_length=32, unique=True)
	batch = models.CharField(max_length=32)
	semester = models.PositiveSmallIntegerField()
	section = models.CharField(max_length=8, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.registration_number} - {self.user.get_full_name() or self.user.username}"


class Faculty(models.Model):
	"""Faculty profile with JNTUH department choices."""
	
	class Department(models.TextChoices):
		CSE = "CSE", _("Computer Science and Engineering")
		ECE = "ECE", _("Electronics and Communication Engineering")
		EEE = "EEE", _("Electrical and Electronics Engineering")
		MECH = "MECH", _("Mechanical Engineering")
		CIVIL = "CIVIL", _("Civil Engineering")
		IT = "IT", _("Information Technology")
		EIE = "EIE", _("Electronics and Instrumentation Engineering")
		CHEM = "CHEM", _("Chemical Engineering")
		MME = "MME", _("Metallurgical and Materials Engineering")
		MINING = "MINING", _("Mining Engineering")
		MATHEMATICS = "MATH", _("Mathematics")
		PHYSICS = "PHY", _("Physics")
		CHEMISTRY = "CHEM_SCI", _("Chemistry")
		ENGLISH = "ENG", _("English")
		MANAGEMENT = "MBA", _("Management Studies")
	
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="faculty_profile")
	employee_number = models.CharField(max_length=32, unique=True)
	department = models.CharField(max_length=64, choices=Department.choices, default=Department.CSE)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "Faculties"

	def __str__(self) -> str:
		return f"{self.employee_number} - {self.user.get_full_name() or self.user.username}"


class Subject(models.Model):
	"""Subject with department association for JNTUH curriculum."""
	code = models.CharField(max_length=16, unique=True)
	name = models.CharField(max_length=128)
	department = models.CharField(max_length=64, choices=Faculty.Department.choices, blank=True)
	semester = models.PositiveSmallIntegerField()
	credits = models.PositiveSmallIntegerField(default=3)
	faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects")

	def __str__(self) -> str:
		return f"{self.code} - {self.name}"


class Attendance(models.Model):
	class Status(models.TextChoices):
		PRESENT = "P", _("Present")
		ABSENT = "A", _("Absent")

	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="attendance_records")
	faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name="attendance_taken")
	date = models.DateField(default=timezone.now)
	status = models.CharField(max_length=1, choices=Status.choices, default=Status.PRESENT)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("student", "subject", "date")
		ordering = ("-date", "student__registration_number")

	def __str__(self) -> str:
		return f"{self.student} - {self.subject} on {self.date}: {self.status}"


class Marks(models.Model):
	class AssessmentType(models.TextChoices):
		IA1 = "IA1", _("Internal Assessment 1")
		IA2 = "IA2", _("Internal Assessment 2")
		IA3 = "IA3", _("Internal Assessment 3")
		ASSIGNMENT = "ASSIGNMENT", _("Assignment")
		LAB = "LAB", _("Lab")

	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
	assessment_type = models.CharField(max_length=16, choices=AssessmentType.choices)
	score = models.DecimalField(max_digits=5, decimal_places=2)
	max_score = models.DecimalField(max_digits=5, decimal_places=2)
	recorded_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-recorded_at",)

	def __str__(self) -> str:
		return f"{self.student} - {self.subject} ({self.assessment_type})"


class Assignment(models.Model):
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
	faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name="assignments")
	title = models.CharField(max_length=128)
	description = models.TextField(blank=True)
	due_date = models.DateField()
	max_score = models.DecimalField(max_digits=5, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("-due_date",)

	def __str__(self) -> str:
		return f"{self.subject}: {self.title}"


class Submission(models.Model):
	class SubmissionStatus(models.TextChoices):
		SUBMITTED = "SUBMITTED", _("Submitted")
		PENDING = "PENDING", _("Pending")
		LATE = "LATE", _("Late")

	assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
	submission_file = models.FileField(
		upload_to="submissions/%Y/%m/%d/", 
		null=True, 
		blank=True,
		help_text="Upload your assignment file (PDF, DOC, ZIP, etc.)"
	)
	submitted_on = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=16, choices=SubmissionStatus.choices, default=SubmissionStatus.PENDING)
	score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	remarks = models.TextField(blank=True)

	class Meta:
		unique_together = ("assignment", "student")
		ordering = ("assignment", "student__registration_number")

	def __str__(self) -> str:
		return f"{self.assignment} - {self.student} ({self.status})"

# Create your models here.
