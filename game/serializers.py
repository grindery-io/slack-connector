from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class CredentialsSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, allow_blank=True)

    class Meta:
        fields = ("access_token",)

    def validate(self, attrs):
        return attrs


class ParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    credentials = CredentialsSerializer()

    class Meta:
        fields = ("key", "credentials")

    def validate(self, attrs):
        return attrs


class ConnectorSerializer(serializers.Serializer):
    method = serializers.CharField()
    id = serializers.CharField()
    params = ParamSerializer()

    default_error_messages = {
        'invalid_type': _('type is invalid.'),
    }

    class Meta:
        fields = ("params", "method", "id")

    def validate(self, attrs):
        return attrs
