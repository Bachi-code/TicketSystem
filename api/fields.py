from rest_framework import ISO_8601
from rest_framework import serializers
from rest_framework.settings import api_settings


class CustomDateTimeField(serializers.DateTimeField):

    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', api_settings.DATETIME_FORMAT)

        if output_format is None or isinstance(value, str):
            return value

        value = self.enforce_timezone(value)

        if output_format.lower() == ISO_8601:
            value = value.isoformat()
            return value
        return value.strftime(output_format)
