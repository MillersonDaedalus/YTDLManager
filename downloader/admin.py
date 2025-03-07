from django.contrib import admin
from .models import DownloadedFiles, DownloadQueue


# Register your models here.
admin.site.register([DownloadedFiles, DownloadQueue])