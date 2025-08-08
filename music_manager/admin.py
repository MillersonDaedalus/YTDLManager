from django.contrib import admin
from .models import *

class AlbumInline(admin.StackedInline):
    model = Album.artists.through

class ArtistAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AlbumInline]

admin.site.register(Artist, ArtistAdmin)

class AlbumAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Album, AlbumAdmin)

class SongAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Song, SongAdmin)

# Register your models here.
admin.site.register([YtmusicAuth, UserFavorite, UserRating])

