import re
import boto3
import os
import hashlib
import logging

from django.db import transaction  
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings

from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from botocore.exceptions import ClientError
from urllib.parse import unquote

from file_upload_system.layout_config import LayoutConfig
from file_upload_system.__init__ import Layout

from .serializers import FileUploadSerializer, FileSerializer
from .models import File, FileAccessLog  


logger = logging.getLogger(__name__)


AWS_REGION_NAME = settings.AWS_REGION_NAME
AWS_BUCKET_NAME = settings.AWS_BUCKET_NAME
AWS_ENCRYPTION_TYPE = settings.AWS_ENCRYPTION_TYPE
AWS_ENCRYPTION_KEY_ID = settings.AWS_ENCRYPTION_KEY_ID
AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY

def hash_user_id(user_id):
    """Hash the user ID using SHA-256."""
    return hashlib.sha256(str(user_id).encode()).hexdigest()

def get_s3_client():
    """Initialize and return an S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME
    )

def sanitize_filename(filename):
    """Sanitize filename to avoid injection attacks but keep spaces."""
    sanitized = re.sub(r'[^\w\.\-\s]', '_', filename)  
    return sanitized.strip()


def handle_file_not_found():
    """Return response for file not found with a generic message."""
    return HttpResponse("File not found or permission denied.", status=404)


@method_decorator(login_required, name='dispatch')
class FilesView(TemplateView):
    template_name = 'pages/files/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = Layout.init(context)
        LayoutConfig.addJavascriptFile('js/files/list.js')
        LayoutConfig.addVendor('datatables')
        files = File.objects.filter(user=self.request.user)
       
        context.update({
            "files": files,
        })
        return context


class FileUploadAPI(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def is_text_file(self, file):
        """Check if the file contains only text characters by verifying UTF-8 encoding and excluding null bytes."""
        try:
            sample = file.read(1024)
            file.seek(0)

            if b'\x00' in sample:
                return False

            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False


    def generate_unique_filename(self, user, filename):
        """Generate a unique sanitized filename by appending a number if it already exists."""
        sanitized_filename = sanitize_filename(filename)
        base, extension = os.path.splitext(sanitized_filename)
        counter = 1
        new_filename = sanitized_filename

        while File.objects.filter(user=user, filename=new_filename).exists():
            new_filename = f"{base} ({counter}){extension}"
            counter += 1

        return new_filename

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            if not uploaded_file.name.endswith('.txt') or uploaded_file.content_type != 'text/plain':
                return Response({"error": "Only .txt files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

            if uploaded_file.size < 512:
                return Response({"error": "File size is too small. Minimum size is 0.5KB."}, status=status.HTTP_400_BAD_REQUEST)

            if uploaded_file.size > 2048:
                return Response({"error": "File size exceeds 2KB limit."}, status=status.HTTP_400_BAD_REQUEST)

            if not self.is_text_file(uploaded_file):
                return Response({'error': 'The file content must be plain text.'}, status=status.HTTP_400_BAD_REQUEST)

            unique_filename = self.generate_unique_filename(request.user, uploaded_file.name)
            s3_client = get_s3_client()
            hashed_user_id = hash_user_id(request.user.id)
            file_key = f"{hashed_user_id}/{unique_filename}"

            try:
                with transaction.atomic():  
                    s3_client.upload_fileobj(
                        uploaded_file,
                        AWS_BUCKET_NAME,
                        file_key,
                        ExtraArgs={
                            "ContentType": "text/plain",
                            "ServerSideEncryption": AWS_ENCRYPTION_TYPE,
                            "SSEKMSKeyId": AWS_ENCRYPTION_KEY_ID
                        }
                    )

                    file_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
                    upload_timestamp = timezone.now()

                    File.objects.create(
                        user=request.user,
                        filename=unique_filename,
                        file_url=file_url,
                        file_size=uploaded_file.size,
                        is_encrypted=True,
                        upload_timestamp=upload_timestamp
                    )
                
                return Response({"status": "File uploaded successfully"}, status=201)
            except ClientError as e:
                logger.error(f"Failed to upload file: {str(e)}")
                return Response({"error": "File upload failed due to server error."}, status=500)

        return Response(serializer.errors, status=400)


class FileDownloadAPI(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_name, *args, **kwargs):
        s3_client = get_s3_client()
        decoded_filename = unquote(file_name)  
        hashed_user_id = hash_user_id(request.user.id)
        file_key = f"{hashed_user_id}/{decoded_filename}"  

        try:
            with transaction.atomic():  
                
                file_record = File.objects.get(filename=decoded_filename, user=request.user)
                file_object = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=file_key)
                file_content = file_object['Body'].read()

                FileAccessLog.objects.create(
                    file=file_record,
                    user=request.user,
                    access_type="download"
                )

            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{decoded_filename}"'
            return response
        except File.DoesNotExist:
            return handle_file_not_found()
        except ClientError as e:
            logger.error(f"Failed to download file: {str(e)}")
            return HttpResponse("Failed to retrieve file.", status=500)


class FileListAPI(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        files = File.objects.filter(user=request.user)
        serializer = FileSerializer(files, many=True)
        return Response({"files": serializer.data}, status=200)


class FileContentAPI(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_name, *args, **kwargs):
        s3_client = get_s3_client()

        decoded_filename = unquote(file_name)  
        hashed_user_id = hash_user_id(request.user.id)
        file_key = f"{hashed_user_id}/{decoded_filename}"  

        try:
            with transaction.atomic():  
                
                file_record = File.objects.get(filename=decoded_filename, user=request.user)
                file_object = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=file_key)
                file_content = file_object['Body'].read().decode('utf-8')
                
                FileAccessLog.objects.create(
                    file=file_record,
                    user=request.user,
                    access_type="view"
                )

            return Response({"file_name": decoded_filename, "content": file_content}, status=200)
        except File.DoesNotExist:
            return handle_file_not_found()
        except ClientError as e:
            logger.error(f"Failed to retrieve file content: {str(e)}")
            return Response({"error": "File retrieval failed."}, status=500)
