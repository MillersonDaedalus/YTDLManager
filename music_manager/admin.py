from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([YtmusicAuth, Artist, Album, Song, UserFavorite, UserRating])