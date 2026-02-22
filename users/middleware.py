"""
Session timeout middleware - Auto logout inactive users
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin


class SessionIdleTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to automatically logout users after period of inactivity.
    Logs out user if they've been inactive for SESSION_COOKIE_AGE seconds.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get last activity time from session
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Convert string to datetime if stored as string
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                
                # Calculate idle time
                idle_time = (datetime.now() - last_activity).total_seconds()
                
                # Get timeout from settings (default 30 minutes)
                timeout = getattr(settings, 'SESSION_COOKIE_AGE', 1800)
                
                # If idle time exceeds timeout, logout user
                if idle_time > timeout:
                    logout(request)
                    request.session.flush()  # Clear all session data
                    return None
            
            # Update last activity time
            request.session['last_activity'] = datetime.now().isoformat()
        
        return None
