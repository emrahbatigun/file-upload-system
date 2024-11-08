from django.contrib import admin
from .models import File, FileAccessLog

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'file_size', 'upload_timestamp', 'is_encrypted')
    search_fields = ('filename', 'user__username')
    list_filter = ('is_encrypted', 'upload_timestamp')

@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'access_timestamp', 'access_type')
    search_fields = ('file__filename', 'user__username')
    list_filter = ('access_type', 'access_timestamp')
