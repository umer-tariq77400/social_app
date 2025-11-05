from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import login_view, dashboard

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path("", dashboard, name="dashboard"),
]
