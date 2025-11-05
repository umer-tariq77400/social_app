from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import LoginForm


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html', {"section": "dashboard"})


def login_view(request):   
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Login successful.")
                else:
                    return HttpResponse("Account disabled.")
            else:
                return HttpResponse("Invalid credentials.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})