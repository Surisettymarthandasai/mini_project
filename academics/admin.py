from django.contrib import admin

from .models import Assignment, Attendance, Faculty, Marks, Student, Subject, Submission


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("registration_number", "user", "batch", "semester", "section")
	search_fields = ("registration_number", "user__username", "user__first_name", "user__last_name")
	list_filter = ("batch", "semester")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
	list_display = ("employee_number", "user", "department")
	search_fields = ("employee_number", "user__username", "user__first_name", "user__last_name", "department")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "semester", "credits", "faculty")
	search_fields = ("code", "name")
	list_filter = ("semester",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ("student", "subject", "date", "status", "faculty")
	list_filter = ("status", "date", "subject")
	search_fields = ("student__registration_number", "subject__code")


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
	list_display = ("student", "subject", "assessment_type", "score", "max_score", "recorded_at")
	list_filter = ("assessment_type", "subject")
	search_fields = ("student__registration_number", "subject__code")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ("title", "subject", "faculty", "due_date", "max_score")
	list_filter = ("due_date", "subject")
	search_fields = ("title", "subject__code", "subject__name")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
	list_display = ("assignment", "student", "status", "submitted_on", "score")
	list_filter = ("status", "assignment")
	search_fields = ("assignment__title", "student__registration_number")

# Register your models here.
