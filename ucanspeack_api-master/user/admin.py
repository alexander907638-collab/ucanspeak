from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *


class UserAdmin(BaseUserAdmin):

    readonly_fields = ['date_joined']

    list_display = (
        'email',
        'full_name',
        'phone',
        'is_school',
        'is_active',
        'date_joined',

    )
    ordering = ('id',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                "full_name",
                'login',
                "email",
                       'password1',
                       'password2',
                       ), }),)
    search_fields = ('id','email', 'full_name', 'phone',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info',
         {'fields': (
             'login',
             'max_logins',
             'is_school',
                "full_name",
                "phone",
                "avatar",
             "subscription_expire",
             "date_joined"
         )}
         ),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups',)}),)


admin.site.register(User,UserAdmin)

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "user_email", "user_login",
        "created", "last_used_at", "expires_at", "is_expired_display",
        "ip_address", "user_agent_short", "short_key",
    )
    list_select_related = ("user",)
    search_fields = (
        "user__email", "user__login", "user__full_name",
        "key", "ip_address",
    )
    list_filter = ("created", "expires_at")
    ordering = ("-created",)
    readonly_fields = ("created", "key", "last_used_at")

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Login", ordering="user__login")
    def user_login(self, obj):
        return obj.user.login

    @admin.display(description="Token")
    def short_key(self, obj):
        return obj.key[:12] + "..."

    @admin.display(description="UA", ordering="user_agent")
    def user_agent_short(self, obj):
        if not obj.user_agent:
            return "-"
        return obj.user_agent[:50] + ("..." if len(obj.user_agent) > 50 else "")

    @admin.display(description="Истёк?", boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired()




@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "admin__email",
        "name",
    )


