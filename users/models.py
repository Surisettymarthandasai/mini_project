from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
	"""Profile extends the base user with a role for authorization checks."""

	class Roles(models.TextChoices):
		ADMIN = "ADMIN", _("Admin")
		FACULTY = "FACULTY", _("Faculty")
		STUDENT = "STUDENT", _("Student")

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.STUDENT)
	is_approved = models.BooleanField(default=False, help_text="Admin approval status")
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		return f"{self.user.username} ({self.role})"

# Create your models here.
