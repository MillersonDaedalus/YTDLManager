from django.urls import path

from . import views

app_name = "music_manager"
urlpatterns = [
    path("", views.index, name="home"),
    #path("<str:user>/", views.requests, name="requests"),
    #path("<str:user>/<int:item_id>/", views.item, name="item"),
    path("manage_artists/", views.manage_artists, name="manage_artists"),
    path("manage_likes/", views.manage_likes, name="manage_likes")
]