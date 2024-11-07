from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=255)
    file_url = models.TextField()
    file_size = models.IntegerField()  # in bytes
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    is_encrypted = models.BooleanField(default=False)

    def __str__(self):
        return self.filename
    

class FileAccessLog(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    access_timestamp = models.DateTimeField(auto_now_add=True)
    access_type = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} - {self.access_type} - {self.file.filename}"