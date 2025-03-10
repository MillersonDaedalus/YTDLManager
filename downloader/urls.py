from django.urls import path

from . import views

app_name = "downloader"
urlpatterns = [
    path("", views.index, name="index"),
    #path("<str:user>/", views.requests, name="requests"),
    path("<str:user>/<int:item_id>/", views.item, name="item"),
    path("example/", views.example, name="example")
]