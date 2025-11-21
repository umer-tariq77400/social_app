from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    dashboard,
    disconnect_social,
    edit,
    register,
    user_detail,
    user_follow,
    user_list,
)

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("", dashboard, name="dashboard"),
    path("register/", register, name="register"),
    path("edit/", edit, name="edit"),
    path("disconnect/<str:backend>/", disconnect_social, name="disconnect_social"),
    path("users/", user_list, name="user_list"),
    path("users/follow/", user_follow, name="user_follow"),
    path("users/<str:username>/", user_detail, name="user_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
