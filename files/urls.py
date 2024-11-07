from django.urls import path
from .views import FileUploadAPI, FilesView, FileDownloadAPI, FileListAPI, FileContentAPI

app_name = 'files'

urlpatterns = [
    path('', FilesView.as_view(template_name='pages/files/index.html'), name='index'),
    path('api/upload/', FileUploadAPI.as_view(), name='api_file_upload'),
    path('api/download/<str:file_name>/', FileDownloadAPI.as_view(), name='api_file_download'),
    path('api/files/', FileListAPI.as_view(), name='api_file_list'),
    path('api/file-content/<str:file_name>/', FileContentAPI.as_view(), name='api_file_content'),
]
