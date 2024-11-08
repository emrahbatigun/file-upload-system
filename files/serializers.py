from rest_framework import serializers
from .models import File


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'filename', 'file_url', 'file_size', 'upload_timestamp', 'is_encrypted')
