from rest_framework import serializers
from .models import UserSession


class UserSessionSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            'id',
            'device_name',
            'browser_name',
            'os_name',
            'ip_address',
            'created_at',
            'last_activity_at',
            'is_current',
        ]
        read_only_fields = fields

    def get_is_current(self, obj):
        current_jti = self.context.get('current_jti')
        return current_jti == obj.refresh_jti
