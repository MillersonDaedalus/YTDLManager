from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Artist, Song, UserRating, UserFavorite


@login_required
def home(request):
    # Get top-rated artists (average rating >= 3, ordered by rating)
    top_artists = Artist.objects.annotate(
        avg_rating=Avg('userrating__rating'),
        rating_count=Count('userrating')
    ).filter(
        userrating__user=request.user,
        userrating__rating__gte=3
    ).order_by('-avg_rating')[:5]

    # Get top-rated songs
    top_songs = Song.objects.annotate(
        avg_rating=Avg('userrating__rating')
    ).filter(
        userrating__user=request.user
    ).order_by('-avg_rating')[:10]

    # Get recently favorited items
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
    # Get all artists the user has rated or favorited
    subscribed_artists = Artist.objects.filter(
        models.Q(userrating__user=request.user) |
        models.Q(userfavorite__user=request.user)
    ).distinct().prefetch_related(
        'albums',
        'albums__songs'
    ).annotate(
        user_rating=Avg('userrating__rating', filter=models.Q(userrating__user=request.user)),
        is_favorite=Exists(UserFavorite.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(Artist),
            object_id=OuterRef('pk')
        ))
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