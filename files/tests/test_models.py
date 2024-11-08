from django.test import TestCase
from django.contrib.auth.models import User
from files.models import File, FileAccessLog


class FileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_file_creation(self):
        file = File.objects.create(
            user=self.user,
            filename='testfile.txt',
            file_url='http://example.com/testfile.txt',
            file_size=1024,
            is_encrypted=True
        )
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(file.filename, 'testfile.txt')
        self.assertEqual(file.user, self.user)
        self.assertTrue(file.is_encrypted)
        self.assertIsNotNone(file.upload_timestamp)

    def test_file_str(self):
        file = File.objects.create(
            user=self.user,
            filename='testfile.txt',
            file_url='http://example.com/testfile.txt',
            file_size=1024,
            is_encrypted=True
        )
        self.assertEqual(str(file), 'testfile.txt')

class FileAccessLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.file = File.objects.create(
            user=self.user,
            filename='testfile.txt',
            file_url='http://example.com/testfile.txt',
            file_size=1024,
            is_encrypted=True
        )

    def test_file_access_log_creation(self):
        log = FileAccessLog.objects.create(
            file=self.file,
            user=self.user,
            access_type='download'
        )
        self.assertEqual(FileAccessLog.objects.count(), 1)
        self.assertEqual(log.file, self.file)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.access_type, 'download')
        self.assertIsNotNone(log.access_timestamp)

    def test_file_access_log_str(self):
        log = FileAccessLog.objects.create(
            file=self.file,
            user=self.user,
            access_type='download'
        )
        expected_str = f"{self.user.username} - {log.access_type} - {self.file.filename}"
        self.assertEqual(str(log), expected_str)
