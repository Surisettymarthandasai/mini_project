from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("pending/", views.pending_users, name="pending_users"),
    path("approve/<int:user_id>/", views.approve_user, name="approve_user"),
    path("reject/<int:user_id>/", views.reject_user, name="reject_user"),
    path("create/", views.create_user, name="create_user"),
    path("api/subjects/<str:department>/", views.get_subjects_by_department, name="get_subjects_by_department"),
]
