from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import login_view, dashboard

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("accounts:password_change_done")
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("", dashboard, name="dashboard"),
    # path('custom-login/', login_view, name='custom_login'),
]
