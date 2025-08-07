from django.urls import path

from . import views

app_name = "music_manager"
urlpatterns = [
    path("", views.home, name="home"),
    #path("<str:user>/", views.requests, name="requests"),
    #path("<str:user>/<int:item_id>/", views.item, name="item"),
    path("manage_artists/", views.manage_artists, name="manage_artists"),
    path("manage_likes/", views.manage_likes, name="manage_likes"),
    path('ytmusic-auth/', views.setup_ytmusic_auth, name='ytmusic_auth'),
    path('ytmusic-callback/', views.ytmusic_callback, name='ytmusic_callback'),
    path('user-information/', views.user_information, name='user_information'),
    path('artists/', views.artists_information, name='artists_information'),
    path('artists/<slug:slug>/', views.artist_info, name='artist_info'),
    path('artists/<slug:slug>/<slug:slug>/', views.album_info, name='album_info')
]