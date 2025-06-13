from django.urls import path

from . import views

app_name = "downloader"
urlpatterns = [
    path("", views.index, name="home"),
    #path("<str:user>/", views.requests, name="requests"),
    #path("<str:user>/<int:item_id>/", views.item, name="item"),
    path("download/", views.download, name="download"),
    path("completed/", views.completed, name="completed")
]