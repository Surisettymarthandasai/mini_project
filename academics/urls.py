from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/<int:pk>/assign-faculty/", views.subject_assign_faculty, name="subject_assign_faculty"),
    path("subjects/<int:pk>/unassign-faculty/", views.subject_unassign_faculty, name="subject_unassign_faculty"),
    path("attendance/", views.attendance_summary, name="attendance_summary"),
    path("attendance/detailed/", views.attendance_detailed, name="attendance_detailed"),
    path("attendance/list/", views.attendance_list, name="attendance_list"),
    path("marks/", views.marks_overview, name="marks_overview"),
    path("attendance/new/", views.attendance_create, name="attendance_create"),
    path("attendance/<int:pk>/edit/", views.attendance_edit, name="attendance_edit"),
    path("attendance/<int:pk>/delete/", views.attendance_delete, name="attendance_delete"),
    path("marks/new/", views.marks_create, name="marks_create"),
    path("marks/<int:pk>/edit/", views.marks_edit, name="marks_edit"),
    path("marks/<int:pk>/delete/", views.marks_delete, name="marks_delete"),
    path("assignments/new/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:pk>/edit/", views.assignment_edit, name="assignment_edit"),
    path("assignments/<int:pk>/delete/", views.assignment_delete, name="assignment_delete"),
    path("submissions/new/", views.submission_create, name="submission_create"),
    path("assignments/", views.assignment_list, name="assignment_list"),
    path("assignments/<int:assignment_id>/submit/", views.student_submit_assignment, name="student_submit_assignment"),
    path("submissions/", views.submission_list, name="submission_list"),
]
