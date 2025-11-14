from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created")
    search_fields = ("title", "description", "user__username")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("created", "user")
    filter_horizontal = ("users_like",)
    ordering = ("-created",)
    readonly_fields = ("created",)
