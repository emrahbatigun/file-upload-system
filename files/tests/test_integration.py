import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from moto import mock_s3
import boto3
from django.conf import settings
from files.models import File, FileAccessLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', email='test@example.com', password='password')


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def test_file():
    content = b'a' * 1024
    return SimpleUploadedFile("test.txt", content, content_type="text/plain")


@pytest.fixture
def s3_bucket():
    with mock_s3():
        s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
        s3.create_bucket(
            Bucket=settings.AWS_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION_NAME}
        )
        yield s3


class TestFileUploadDownloadIntegration:
    def test_upload_and_download(self, authenticated_client, test_file, user, s3_bucket):
        upload_url = reverse('files:api_file_upload')
        upload_data = {'file': test_file}
        response = authenticated_client.post(upload_url, upload_data, format='multipart')

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.content}"
        assert response.data['status'] == 'File uploaded successfully'

        assert File.objects.filter(user=user, filename='test.txt').exists()
        file_record = File.objects.get(user=user, filename='test.txt')

        test_file.seek(0)
        
        download_url = reverse('files:api_file_download', kwargs={'file_name': 'test.txt'})
        download_response = authenticated_client.get(download_url)
        assert download_response.status_code == 200

        test_file.seek(0)
        assert download_response.content == test_file.read()
        assert download_response['Content-Disposition'] == f'attachment; filename="test.txt"'

        assert FileAccessLog.objects.filter(file=file_record, user=user, access_type='download').exists()

    def test_view_file_content(self, authenticated_client, test_file, user, s3_bucket):
        upload_url = reverse('files:api_file_upload')
        upload_data = {'file': test_file}
        response = authenticated_client.post(upload_url, upload_data, format='multipart')
        assert response.status_code == 201

        content_url = reverse('files:api_file_content', kwargs={'file_name': 'test.txt'})
        content_response = authenticated_client.get(content_url)
        assert content_response.status_code == 200
        assert content_response.data['file_name'] == 'test.txt'

        test_file.seek(0)
        assert content_response.data['content'] == test_file.read().decode('utf-8')

        file_record = File.objects.get(user=user, filename='test.txt')
        assert FileAccessLog.objects.filter(file=file_record, user=user, access_type='view').exists()
