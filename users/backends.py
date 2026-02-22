from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class ApprovedUserBackend(ModelBackend):
    """Custom authentication backend that only allows approved users to login."""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        # Check password
        if user.check_password(password):
            # Check if user has a profile and is approved
            try:
                if not user.profile.is_approved:
                    return None  # User not approved
            except AttributeError:
                # User doesn't have a profile (e.g., superuser)
                pass
            
            # Check if user is active
            if not user.is_active:
                return None
            
            return user
        
        return None
