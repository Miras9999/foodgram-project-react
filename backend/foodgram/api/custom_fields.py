import base64
import os
import random

from rest_framework import serializers
from django.conf import settings


charachters = 'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz1234567890'


class CustomImageField(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            parse = data.split(',')
            data = parse[1]
            decoded_data = base64.b64decode(data)
        except Exception:
            raise serializers.ValidationError("Invalid base64 data.")
        file_extension = 'png'
        name = f"{''.join(random.choices(charachters, k=6))}.{file_extension}"
        path = os.path.join(settings.MEDIA_ROOT, 'recipes', 'images', name)
        try:
            with open(path, 'wb') as file:
                file.write(decoded_data)
            return os.path.join('recipes', 'images', name)
        except Exception as e:
            print(e)
            raise serializers.ValidationError("Failed to save the image file.")
