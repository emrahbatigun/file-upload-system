import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from moto import mock_s3
import boto3
from django.conf import settings
import hashlib
from files.models import File

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


class TestFileUploadAPI:
    def test_file_upload_success(self, authenticated_client, test_file, s3_bucket):
        url = reverse('files:api_file_upload')
        data = {'file': test_file}
        response = authenticated_client.post(url, data, format='multipart')
        print(response.status_code)
        print(response.content)  # Add this line
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'File uploaded successfully'

    def test_file_upload_unauthenticated(self, api_client, test_file):
        url = reverse('files:api_file_upload')
        data = {'file': test_file}
        response = api_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_file_upload_invalid_file_type(self, authenticated_client, s3_bucket):
        invalid_file = SimpleUploadedFile("test.jpg", b"Sample image content", content_type="image/jpeg")
        url = reverse('files:api_file_upload')
        data = {'file': invalid_file}
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Only .txt files are allowed.' in response.data['error']

    def test_file_upload_invalid_file_content(self, authenticated_client, s3_bucket):
        invalid_content = SimpleUploadedFile("test.txt", b"\x00" * 512, content_type="text/plain")
        url = reverse('files:api_file_upload')
        data = {'file': invalid_content}
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'The file content must be plain text.' in response.data['error']

    def test_file_upload_too_small(self, authenticated_client, s3_bucket):
        small_file = SimpleUploadedFile("test.txt", b"a"*100, content_type="text/plain")  # 100 bytes
        url = reverse('files:api_file_upload')
        data = {'file': small_file}
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'File size is too small. Minimum size is 0.5KB.' in response.data['error']

    def test_file_upload_too_large(self, authenticated_client, s3_bucket):
        large_file = SimpleUploadedFile("test.txt", b"a"*3000, content_type="text/plain")  # 3KB
        url = reverse('files:api_file_upload')
        data = {'file': large_file}
        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'File size exceeds 2KB limit.' in response.data['error']


class TestFileDownloadAPI:
    def test_file_download_success(self, authenticated_client, user, s3_bucket):
        s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
        file_content = b"Sample file content"
        file_name = 'test.txt'
        hashed_user_id = hashlib.sha256(str(user.id).encode()).hexdigest()
        file_key = f"{hashed_user_id}/{file_name}"
        s3.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_key, Body=file_content)
        File.objects.create(
            user=user,
            filename=file_name,
            file_url=f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{file_key}",
            file_size=len(file_content),
            is_encrypted=True
        )
        url = reverse('files:api_file_download', kwargs={'file_name': file_name})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.content == file_content
        assert response['Content-Disposition'] == f'attachment; filename="{file_name}"'

    def test_file_download_not_found(self, authenticated_client):
        url = reverse('files:api_file_download', kwargs={'file_name': 'nonexistent.txt'})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'File not found or permission denied.' in response.content.decode()

    def test_file_download_unauthenticated(self, api_client):
        url = reverse('files:api_file_download', kwargs={'file_name': 'test.txt'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestFileContentAPI:
    def test_file_content_success(self, authenticated_client, user, s3_bucket):
        s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
        file_content = b"Sample file content"
        file_name = 'test.txt'
        hashed_user_id = hashlib.sha256(str(user.id).encode()).hexdigest()
        file_key = f"{hashed_user_id}/{file_name}"
        s3.put_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_key, Body=file_content)
        File.objects.create(
            user=user,
            filename=file_name,
            file_url=f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{file_key}",
            file_size=len(file_content),
            is_encrypted=True
        )
        url = reverse('files:api_file_content', kwargs={'file_name': file_name})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['file_name'] == file_name
        assert response.data['content'] == file_content.decode('utf-8')

    def test_file_content_not_found(self, authenticated_client):
        url = reverse('files:api_file_content', kwargs={'file_name': 'nonexistent.txt'})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'File not found or permission denied.' in response.content.decode()

    def test_file_content_unauthenticated(self, api_client):
        url = reverse('files:api_file_content', kwargs={'file_name': 'test.txt'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFileListAPI:
    def test_file_list_success(self, authenticated_client, user):
        File.objects.create(
            user=user,
            filename='test1.txt',
            file_url='http://example.com/test1.txt',
            file_size=1024,
            is_encrypted=True
        )
        File.objects.create(
            user=user,
            filename='test2.txt',
            file_url='http://example.com/test2.txt',
            file_size=2048,
            is_encrypted=True
        )
        url = reverse('files:api_file_list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        files = response.data['files']
        assert len(files) == 2

    def test_file_list_empty(self, authenticated_client):
        url = reverse('files:api_file_list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        files = response.data['files']
        assert len(files) == 0

    def test_file_list_unauthenticated(self, api_client):
        url = reverse('files:api_file_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
