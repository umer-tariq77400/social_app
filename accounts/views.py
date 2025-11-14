from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib import messages
from social_django.models import UserSocialAuth
import os


@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error updating your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        "accounts/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def dashboard(request):
    # Load bookmarklet code from file
    bookmarklet_file = os.path.join(
        settings.BASE_DIR, "images", "templates", "bookmarklet_launcher.js"
    )
    with open(bookmarklet_file, "r") as f:
        bookmarklet_code = "javascript:" + f.read().strip()

    return render(
        request,
        "accounts/dashboard.html",
        {"section": "dashboard", "bookmarklet_code": bookmarklet_code},
    )


@login_required
def disconnect_social(request, backend):
    """Disconnect a social account from user account."""
    if request.method == "POST":
        try:
            # Get the social auth connection
            social_auth = UserSocialAuth.objects.get(
                user=request.user, provider=backend
            )
            social_auth.delete()
            messages.success(
                request, f"Successfully disconnected your {backend} account"
            )
        except UserSocialAuth.DoesNotExist:
            messages.warning(request, f"No {backend} account connected to your profile")
        except Exception as e:
            messages.error(request, f"Error disconnecting account: {str(e)}")

        return redirect("dashboard")

    # GET request - show confirmation page
    return render(request, "accounts/disconnect_confirm.html", {"backend": backend})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data["password"])
            # Save the User object
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            return render(
                request, "accounts/register_done.html", {"new_user": new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"user_form": user_form})
