from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class ParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    authentication = serializers.CharField(required=False)
    cdsName = serializers.CharField(required=False)

    class Meta:
        fields = ("key", "fieldData", "authentication")

    def validate(self, attrs):
        key = attrs.get("key")
        authentication = attrs.get("authentication")
        # attrs['key'] = key
        # attrs['authentication'] = authentication
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
