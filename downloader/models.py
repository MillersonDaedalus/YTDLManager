from django.db import models


# Create your models here.
class DownloadedFiles(models.Model):
    user = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=200, blank=True, null=True)
    author_url = models.URLField(max_length=500)
    playlist = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url

class DownloadQueue(models.Model):
    user = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, )
    finished_at = models.DateTimeField(blank=True, null=True)