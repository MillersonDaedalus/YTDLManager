import ytmusicapi
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import CASCADE
from django.conf import settings
from ytmusicapi import YTMusic, OAuthCredentials
import os
import logging

logger = logging.getLogger(__name__)

def user_auth_upload_path(instance, filename):
    """Generate upload path with proper error handling"""
    try:
        if not instance.user_id:
            raise ValueError("User instance is not saved yet")

        # Ensure filename is safe
        filename = os.path.basename(filename)
        path = os.path.join("ytmusic_auth", str(instance.user_id), filename)

        logger.debug(f"Generated upload path: {path}")
        return path

    except Exception as e:
        logger.error(f"Error generating upload path: {str(e)}")
        raise  # Re-raise the exception after logging


# Create your models here.
class YtmusicAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ytmusic_auth')
    auth_file = models.FileField(upload_to=user_auth_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_updated_info = models.BooleanField(default=False)

    def __str__(self):
        return f"YouTube Music Auth for {self.user.username}"

    @classmethod
    def create_oauth_file(cls, user):
        """Encapsulated OAuth file creation with proper cleanup"""
        try:
            logger.info(f"Creating OAuth file for user {user.id}")

            # Delete any existing auth first
            cls.objects.filter(user=user).delete()

            # Generate paths
            filename = "oauth.json"
            relative_path = user_auth_upload_path(cls(user=user), filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            logger.debug(f"Full target path: {full_path}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Create the OAuth file
            ytmusicapi.setup_oauth(
                client_id=settings.YTMUSIC_CLIENT_ID,
                client_secret=settings.YTMUSIC_CLIENT_SECRET,
                filepath=full_path,
                open_browser=True
            )
            logger.info("OAuth file created successfully")

            # Create model instance
            auth = cls(user=user)
            auth.auth_file.name = relative_path
            auth.save()

            return auth

        except Exception as e:
            logger.error(f"Failed to create OAuth file: {str(e)}")

            # Clean up if file was created but model wasn't saved
            if os.path.exists(full_path):
                os.remove(full_path)

            raise  # Re-raise the exception after cleanup

    def get_ytmusic_client(self):
        """
        Returns an authenticated YTMusic instance using the stored OAuth file
        """
        try:
            # Get the full filesystem path to the auth file
            auth_path = self.auth_file.path
            return YTMusic(auth_path, oauth_credentials=OAuthCredentials(settings.YTMUSIC_CLIENT_ID,settings.YTMUSIC_CLIENT_SECRET))
        except Exception as e:
            # Handle cases where the file might be missing or corrupted
            raise YTMusicAuthError(f"Failed to initialize YTMusic client: {str(e)}")

class YTMusicAuthError(Exception):
    """Custom exception for YTMusic auth related errors"""
    pass

# join tables from users
class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Generic foreign key approach to rate different content types
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    rating = models.IntegerField(
        validators=[MinValueValidator(-5), MaxValueValidator(5)],
        help_text="Rating from -5 (strong dislike) to 5 (absolute favorite)"
    )
    is_recommended = models.BooleanField(default=False)
    date_rated = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = "User Rating"
        verbose_name_plural = "User Ratings"

    def __str__(self):
        return f"{self.user.username}'s rating for {self.content_object}"


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Generic foreign key approach to favorite different content types
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date_favorited = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = "User Favorite"
        verbose_name_plural = "User Favorites"

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.content_object}"




# -------------------------------

class Artist(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True)
    channelId = models.CharField(max_length=255, unique=True,)
    album_browseId = models.CharField(max_length=255, default='None', null=True)
    album_params = models.CharField(max_length=255, default='None', null=True)
    number_of_albums = models.PositiveIntegerField(blank=True, null=True)
    singles_browseId = models.CharField(max_length=255, default='None', null=True)
    singles_params = models.CharField(max_length=255, default='None', null=True)
    number_of_singles = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    need_discography = models.BooleanField(default=True)


    def __str__(self):
        return self.name



    def populate(self, artist_info):
        self.name = artist_info['name']
        self.channelId = artist_info['channelId']
        self.bio = artist_info['description']
        if 'albums' in artist_info and artist_info['albums']['browseId'] is not None:
            self.album_browseId = artist_info['albums']['browseId']
            if 'params' in artist_info['albums']:
                self.album_params = artist_info['albums']['params']
            else:
                self.album_params = 'None'
        else:
            self.album_browseId = 'None'
        if 'singles' in artist_info and artist_info['singles']['browseId'] is not None:
            self.singles_browseId = artist_info['singles']['browseId']
            if 'params' in artist_info['singles']:
                self.singles_params = artist_info['singles']['params']
            else:
                self.singles_params = 'None'
        else:
            self.singles_browseId = 'None'

    def get_discography(self, ytmusic_client):
        albums = []
        if self.album_params != 'None':
            albums.extend(ytmusic_client.get_artist_albums(self.album_browseId, self.album_params))
        else:
            artist_info = ytmusic_client.get_artist(self.channelId)
            if 'albums' in artist_info:
                albums.extend(artist_info['albums']['results'])
        if self.singles_params != 'None':
            albums.extend(ytmusic_client.get_artist_albums(self.singles_browseId, self.singles_params))
        else:
            artist_info = ytmusic_client.get_artist(self.channelId)
            if 'singles' in artist_info:
                albums.extend(artist_info['singles']['results'])

        if self.need_discography:
            self.make_albums(albums, ytmusic_client)
            self.need_discography = False
            self.save()
        return albums


    def make_albums(self, albums, ytmusic_client):
        for album in albums:
            new_album, created = Album.objects.get_or_create(browseId=album['browseId'])
            print('\t album :', new_album.title, 'new :', created)
            if created:
                album_info = ytmusic_client.get_album(album['browseId'])
                new_album.populate(album_info)
                new_album.save()
                new_album.artists.add(self)
                new_album.save()



class Album(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True)
    artists = models.ManyToManyField(Artist, related_name='albums')
    release_year = models.PositiveIntegerField(blank=True, null=True)
    number_of_songs = models.PositiveIntegerField(blank=True, null=True)
    isExplicit = models.BooleanField(default=False)
    browseId = models.CharField(max_length=255, default='None')
    cover_art = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    catalog_number = models.CharField(max_length=50, blank=True, null=True)
    need_tracks = models.BooleanField(default=True)

    # For album types (standard, deluxe, re-release, etc.)
    ALBUM_TYPES = [
        ('LP', 'Album'),
        ('EP', 'EP'),
        ('SS', 'Single'),
        ('CP', 'Compilation'),
        ('RM', 'Remix'),
        ('DL', 'Deluxe'),
        ('RV', 'Reissue'),
    ]
    album_type = models.CharField(max_length=2, choices=ALBUM_TYPES, default='LP')

    def __str__(self):
        return f"{self.title}"

    def populate(self, album_info):
        self.title = album_info['title']
        self.album_type = album_info['type']
        self.release_year = album_info['year']
        self.number_of_songs = album_info['trackCount']
        self.isExplicit = album_info['isExplicit']

    def get_tracks(self, ytmusic_client):
        tracks = ytmusic_client.get_album(self.browseId)['tracks']

        if self.need_tracks:
            self.make_tracks(tracks)
            self.need_tracks=False
            self.save()

        return tracks

    def make_tracks(self, tracks, ytmusic_client):
        for track in tracks:
            new_track, created = Song.objects.get_or_create(videoId=track['videoId'])
            if created:
                track_info = ytmusic_client.get_song(track['videoId'])
                new_track.populate(track_info)
                new_track.save()
                new_track.albums.add(self)
                new_track.primary_artists.add(self.artists)
                new_track.save()




class Song(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True)
    videoId = models.CharField(max_length=255, default=None)
    url = models.URLField(default=None)
    albums = models.ManyToManyField(Album, related_name='songs', through='AlbumSong')
    primary_artists = models.ManyToManyField(Artist, related_name='songs_as_primary')
    featured_artists = models.ManyToManyField(Artist, related_name='songs_as_featured', blank=True)
    duration = models.DurationField()
    isrc = models.CharField(max_length=12, blank=True, null=True)  # International Standard Recording Code
    lyrics = models.TextField(blank=True, null=True)
    composition_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title

    def populate(self, song_info):
        song_details = song_info['videoDetails']
        self.title = song_details['title']
        self.videoId = song_details['videoId']
        self.url = song_info['microformat']['microformatDataRenderer']['urlCanonical']
        self.duration = song_details['lengthSeconds']

# Intermediate model for Album-Song relationship to track additional data
class AlbumSong(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    track_number = models.PositiveIntegerField()
    disc_number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['disc_number', 'track_number']
        unique_together = ('album', 'song', 'disc_number', 'track_number')

    def __str__(self):
        return f"{self.album.title} - Disc {self.disc_number} Track {self.track_number}: {self.song.title}"





def add_to_artist_class(cls):
    @property
    def average_rating(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import UserRating
        ct = ContentType.objects.get_for_model(self)
        ratings = UserRating.objects.filter(content_type=ct, object_id=self.id)
        if ratings.exists():
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return None

    @property
    def is_favorite(self, user):
        if not user.is_authenticated:
            return False
        from django.contrib.contenttypes.models import ContentType
        from .models import UserFavorite
        ct = ContentType.objects.get_for_model(self)
        return UserFavorite.objects.filter(
            user=user,
            content_type=ct,
            object_id=self.id
        ).exists()

    cls.average_rating = average_rating
    cls.is_favorite = is_favorite
    return cls


# Apply to all three model classes
Artist = add_to_artist_class(Artist)
Album = add_to_artist_class(Album)
Song = add_to_artist_class(Song)