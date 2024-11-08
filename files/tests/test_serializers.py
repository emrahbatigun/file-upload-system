from django.test import TestCase
from files.serializers import FileUploadSerializer
from django.core.files.uploadedfile import SimpleUploadedFile


class FileUploadSerializerTest(TestCase):
    def test_valid_serializer(self):
        test_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        data = {'file': test_file}
        serializer = FileUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer_no_file(self):
        data = {}
        serializer = FileUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)
