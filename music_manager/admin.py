from django.contrib import admin
from .models import *

class AlbumInline(admin.StackedInline):
    model = Album.artists.through

class ArtistAdmin(admin.ModelAdmin):
    inlines = [AlbumInline]

admin.site.register(Artist, ArtistAdmin)

class SongInline(admin.StackedInline):
    model = Song.albums.through

class AlbumAdmin(admin.ModelAdmin):
    inlines = [SongInline]

admin.site.register(Album, AlbumAdmin)

class SongAdmin(admin.ModelAdmin):
    fields = ['title', 'primary_artists', 'videoId']


admin.site.register(Song, SongAdmin)

# Register your models here.
admin.site.register([YtmusicAuth, AlbumSong, UserFavorite, UserRating])

