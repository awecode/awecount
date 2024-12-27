import base64

import six
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            try:
                file_name, data = data.values()
            except Exception:
                return data

            if isinstance(data, six.string_types):
                if "data:" in data and ";base64," in data:
                    header, data = data.split(";base64,")

                try:
                    decoded_file = base64.b64decode(data)
                except TypeError:
                    self.fail("File cannot be saved.")
                except Exception:
                    return data

                data = ContentFile(decoded_file, name=file_name)

            return super(Base64FileField, self).to_internal_value(data)
        return data
