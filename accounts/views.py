import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from social_django.models import UserSocialAuth

from .forms import ProfileEditForm, UserEditForm, UserRegistrationForm
from .models import Contact, Profile


@login_required
def edit(request):
    """Edit user profile""" 
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


User = get_user_model()
@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(
        request,
        "accounts/user/list.html",
        {"section": "people", "users": users}
    )


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        "accounts/user/detail.html",
        {"section": "people", "user": user}
    )


@login_required
def user_follow(request):
    """Handle follow/unfollow actions via AJAX."""
    if request.method == "POST":
        user_id = request.POST.get("id")
        user_to_follow = get_object_or_404(User, id=user_id, is_active=True)
        
        if user_to_follow == request.user:
            return JsonResponse({"status": "error", "message": "You cannot follow yourself"}, status=400)
        
        action = request.POST.get("action")
        
        try:
            if action == "follow":
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user_to_follow
                )
            elif action == "unfollow":
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user_to_follow
                ).delete()
            else:
                return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)
            
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
