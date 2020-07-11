from rest_framework import serializers
from .models import HookNotification


class HookNotificationSerializer(serializers.ModelSerializer):
    # noinspection SpellCheckingInspection
    class Meta:
        model = HookNotification
        fields = '__all__'
