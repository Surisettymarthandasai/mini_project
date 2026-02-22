from users.models import Profile


def user_role(request):
    """Context processor to safely add user role to template context."""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            # Only return role if user is approved (or is superuser/admin)
            if profile.is_approved or request.user.is_superuser or profile.role == Profile.Roles.ADMIN:
                role = profile.role
            else:
                role = "PENDING"
        except (Profile.DoesNotExist, AttributeError):
            role = Profile.Roles.ADMIN if request.user.is_superuser else None
        return {"user_role": role}
    return {"user_role": None}
