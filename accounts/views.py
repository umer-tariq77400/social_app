from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import LoginForm


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html', {"section": "dashboard"})