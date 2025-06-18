import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Exists, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType
from .models import *
from .utils.ytmusic import get_user_ytmusic_client
from ytmusicapi import YTMusic


@login_required
def setup_ytmusic_auth(request):
    if request.method == 'POST':
        try:
            auth = YtmusicAuth.create_oauth_file(request.user)
            messages.success(request, 'YouTube Music OAuth setup successfully!')
            return redirect('music_manager:profile')  # Replace with your desired redirect
        except Exception as e:
            messages.error(request, f'Failed to setup OAuth: {str(e)}')
            return redirect('/ytmusic-auth/')

    # GET request - show setup page
    has_auth = YtmusicAuth.objects.filter(user=request.user).exists()
    return render(request, 'music_manager/ytmusic_auth.html', {
        'has_auth': has_auth
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

@login_required
def user_playlists(request):
    try:
        ytmusic = get_user_ytmusic_client(request.user)
        playlists = ytmusic.get_library_playlists()
        return render(request, 'playlists.html', {'playlists': playlists})
    except YTMusicAuthError as e:
        # Redirect to setup page if auth isn't configured
        return render(request, 'error.html', {
            'error': str(e),
            'redirect_url': '/setup-oauth/'
        })

@login_required
def user_information(request):
    try:
        print("getting user ytmusic client")
        ytmusic = get_user_ytmusic_client(request.user)

        user_artists = ytmusic.get_library_subscriptions(limit=300)
        for i in user_artists:
            artist_info = ytmusic.get_artist(i['browseId'])
            artist_channelId = artist_info['channelId']
            if not Artist.objects.filter(channelId=artist_channelId):
                new_artist = Artist(name=artist_info['name'], channelId=artist_channelId, bio=artist_info['description'])
                new_artist.save()
            artist_albums = ytmusic.get_artist_albums(artist_channelId)

        return redirect('/manage_artists/')



    except YTMusicAuthError as e:
        # Redirect to setup page if auth isn't configured
        return redirect('/ytmusic-auth/')