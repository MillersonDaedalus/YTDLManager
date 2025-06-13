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
                client_id=settings.YTMUSIC_client_id,
                client_secret=settings.YTMUSIC_client_secret,
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
    bio = models.TextField(blank=True, null=True)
    formed_date = models.DateField(blank=True, null=True)
    disbanded_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)


    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=255)
    artists = models.ManyToManyField(Artist, related_name='albums')
    release_date = models.DateField()
    cover_art = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    catalog_number = models.CharField(max_length=50, blank=True, null=True)

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


class Song(models.Model):
    title = models.CharField(max_length=255)
    albums = models.ManyToManyField(Album, related_name='songs', through='AlbumSong')
    primary_artists = models.ManyToManyField(Artist, related_name='songs_as_primary')
    featured_artists = models.ManyToManyField(Artist, related_name='songs_as_featured', blank=True)
    duration = models.DurationField()
    isrc = models.CharField(max_length=12, blank=True, null=True)  # International Standard Recording Code
    lyrics = models.TextField(blank=True, null=True)
    composition_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


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