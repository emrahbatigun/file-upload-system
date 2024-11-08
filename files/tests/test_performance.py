import boto3
import pytest
import hashlib
import time

from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from moto import mock_s3
from django.conf import settings
from files.models import File

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='performancetestuser', email='performance@example.com', password='password')

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def large_test_file():
    content = b"a" * 2047
    return SimpleUploadedFile("large_test.txt", content, content_type="text/plain")

@pytest.fixture
def s3_bucket():
    with mock_s3():
        s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
        s3.create_bucket(
            Bucket=settings.AWS_BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION_NAME}
        )
        yield s3


class TestPerformance:

    def test_file_upload_performance(self, authenticated_client, large_test_file, s3_bucket):
        url = reverse('files:api_file_upload')
        data = {'file': large_test_file}

        start_time = time.time()
        response = authenticated_client.post(url, data, format='multipart')
        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 201
        assert duration < 2

    def test_file_download_performance(self, authenticated_client, user, s3_bucket):
        s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
        file_content = b"a" * 2047
        file_name = 'large_test.txt'
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

        start_time = time.time()
        response = authenticated_client.get(url)
        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 200
        assert duration < 2
