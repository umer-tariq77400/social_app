from django.contrib.auth.models import User
from accounts.models import Profile


class EmailAuthBackend:
    """Authenticate using an email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def get_or_create_user_by_email(backend, details, user=None, *args, **kwargs):
    """
    Get or create user by email address.
    This ensures that if a user disconnects and reconnects with the same OAuth provider,
    they get their original account back instead of creating a duplicate.
    """
    if user:
        # User already exists, return it
        return {"user": user}

    email = details.get("email")
    if not email:
        # No email provided, let the default pipeline handle it
        return {}

    try:
        # Check if a user with this email already exists
        existing_user = User.objects.get(email=email)
        return {"user": existing_user}
    except User.DoesNotExist:
        # User doesn't exist, let the default pipeline create one
        return {}
    except User.MultipleObjectsReturned:
        # Multiple users with same email - log this and let default pipeline handle it
        return {}


def create_profile(backend, user, response, *args, **kwargs):
    """Create a user profile after social authentication."""
    if backend.name == "google-oauth2":
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            profile.bio = "This is my bio"
            profile.save()
        return {"profile": profile}
    return {}


def disconnect_profile(backend, user, *args, **kwargs):
    """
    Clean up user profile when disconnecting social account.
    NOTE: We do NOT delete the profile here to preserve user data.
    The profile remains associated with the user account.
    """
    # Intentionally NOT deleting the profile
    # This allows users to reconnect and keep their data
    return {}
