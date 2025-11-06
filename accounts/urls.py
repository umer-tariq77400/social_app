from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard, register, edit

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', dashboard, name="dashboard"),
    path('register/', register, name="register"),
    path('edit/', edit, name="edit"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
