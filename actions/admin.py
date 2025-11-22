from django.contrib import admin
from .models import Action

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'verb', 'created', 'target')
    search_fields = ('user__username', 'verb')
    list_filter = ('created',)
    date_hierarchy = 'created'