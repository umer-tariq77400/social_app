from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard, register, edit, disconnect_social

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("", dashboard, name="dashboard"),
    path("register/", register, name="register"),
    path("edit/", edit, name="edit"),
    path("disconnect/<str:backend>/", disconnect_social, name="disconnect_social"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
