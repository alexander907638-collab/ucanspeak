from django.contrib import admin
from .models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'ip_address', 'last_activity_at', 'created_at']
    list_filter = ['browser_name', 'os_name', 'created_at']
    search_fields = ['user__email', 'ip_address', 'device_name']
    readonly_fields = ['refresh_jti', 'user_agent', 'created_at', 'last_activity_at']
