import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Exists, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType
from .models import YtmusicAuth, Artist, Album, Song, UserRating, UserFavorite
from .forms import YTMusicAuthForm
from ytmusicapi import YTMusic


@login_required
def setup_ytmusic_auth(request):
    try:
        existing_auth = YtmusicAuth.objects.get(user=request.user)
    except YtmusicAuth.DoesNotExist:
        existing_auth = None

    if request.method == 'POST':
        form = YTMusicAuthForm(request.POST, request.FILES, instance=existing_auth)
        if form.is_valid():
            auth = form.save(commit=False)
            auth.user = request.user
            auth.save()

            # Verify the auth file works
            try:
                auth_file_path = os.path.join(settings.MEDIA_ROOT, auth.auth_file.name)
                YTMusic(auth_file_path)
                messages.success(request, 'YouTube Music authentication setup successfully!')
                return redirect('music_manager:profile')  # Replace with your desired redirect
            except Exception as e:
                auth.delete()  # Remove the invalid auth file
                messages.error(request, f'Authentication failed: {str(e)}')
    else:
        form = YTMusicAuthForm(instance=existing_auth)

    return render(request, 'music_manager/setup_auth.html', {
        'form': form,
        'has_auth': existing_auth is not None
    })


@login_required
def ytmusic_callback(request):
    # This would handle the OAuth callback if needed
    # Implementation depends on how ytmusicapi handles the flow
    pass

@login_required
def home(request):
    artist_content_type = ContentType.objects.get_for_model(Artist)
    song_content_type = ContentType.objects.get_for_model(Song)

    # Top artists
    top_artist_ids = UserRating.objects.filter(
        user=request.user,
        content_type=artist_content_type,
        rating__gte=3
    ).values('object_id').annotate(
        avg_rating=Avg('rating'),
        rating_count=Count('id')
    ).order_by('-avg_rating')[:5].values_list('object_id', flat=True)

    top_artists = Artist.objects.filter(id__in=top_artist_ids).annotate(
        avg_rating=Subquery(
            UserRating.objects.filter(
                user=request.user,
                content_type=artist_content_type,
                object_id=OuterRef('pk')
            ).values('object_id').annotate(
                avg=Avg('rating')
            ).values('avg')[:1]
        )
    ).order_by('-avg_rating')

    # Top songs
    top_song_ids = UserRating.objects.filter(
        user=request.user,
        content_type=song_content_type
    ).values('object_id').annotate(
        avg_rating=Avg('rating')
    ).order_by('-avg_rating')[:10].values_list('object_id', flat=True)

    top_songs = Song.objects.filter(id__in=top_song_ids).annotate(
        avg_rating=Subquery(
            UserRating.objects.filter(
                user=request.user,
                content_type=song_content_type,
                object_id=OuterRef('pk')
            ).values('object_id').annotate(
                avg=Avg('rating')
            ).values('avg')[:1]
        )
    ).order_by('-avg_rating')

    # Recent favorites (unchanged)
    recent_favorites = UserFavorite.objects.filter(
        user=request.user
    ).order_by('-date_favorited')[:5]

    context = {
        'top_artists': top_artists,
        'top_songs': top_songs,
        'recent_favorites': recent_favorites,
    }
    return render(request, 'music_manager/home.html', context)

@login_required
def manage_artists(request):
    artist_content_type = ContentType.objects.get_for_model(Artist)

    # Get artist IDs that have either ratings or favorites
    rated_artist_ids = UserRating.objects.filter(
        user=request.user,
        content_type=artist_content_type
    ).values_list('object_id', flat=True).distinct()

    favorited_artist_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=artist_content_type
    ).values_list('object_id', flat=True).distinct()

    all_artist_ids = set(rated_artist_ids).union(set(favorited_artist_ids))

    subscribed_artists = Artist.objects.filter(
        id__in=all_artist_ids
    ).prefetch_related(
        'albums',
        'albums__songs'
    ).annotate(
        user_rating=Subquery(
            UserRating.objects.filter(
                user=request.user,
                content_type=artist_content_type,
                object_id=OuterRef('pk')
            ).values('object_id').annotate(
                avg=Avg('rating')
            ).values('avg')[:1]
        ),
        is_favorite=Exists(
            UserFavorite.objects.filter(
                user=request.user,
                content_type=artist_content_type,
                object_id=OuterRef('pk')
            )
        )
    ).order_by('-is_favorite', '-user_rating', 'name')

    context = {
        'subscribed_artists': subscribed_artists,
    }
    return render(request, 'music_manager/manage_artists.html', context)


@login_required
def manage_likes(request):
    # Get all favorited items
    favorites = UserFavorite.objects.filter(
        user=request.user
    ).select_related('content_type').order_by('-date_favorited')

    # Organize favorites by type
    favorited_artists = []
    favorited_albums = []
    favorited_songs = []

    for fav in favorites:
        obj = fav.content_object
        if isinstance(obj, Artist):
            favorited_artists.append(obj)
        elif isinstance(obj, Album):
            favorited_albums.append(obj)
        elif isinstance(obj, Song):
            favorited_songs.append(obj)

    context = {
        'favorited_artists': favorited_artists,
        'favorited_albums': favorited_albums,
        'favorited_songs': favorited_songs,
    }
    return render(request, 'music_manager/manage_likes.html', context)