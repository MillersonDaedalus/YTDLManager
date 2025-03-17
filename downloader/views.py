import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from yt_dlp import YoutubeDL
from .models import *
from .forms import *

# Create your views here.
def index(request):
    queue = DownloadQueue.objects.all()
    form = SubmitUrl

    context = {
        "items_in_queue" : queue,
        "form" : form
    }
    #output = "There are ",str(len(queue))," downloads in the queue right now \n",", ".join(q.url for q in queue)
    return render(request, "downloader/index.html", context)


def download(request):
    if request.method == "POST":
        form = SubmitUrl(request.POST)

        if form.is_valid():
            URL = form.cleaned_data["url"]
            print(URL)

            info = YoutubeDL().extract_info(url=URL, download=False)

            print(json.dumps(YoutubeDL.sanitize_info(info)))

    return render(request, "downloader/download.html")


def item(request, user, item_id):
    item = DownloadedFiles.objects.get(id__exact=item_id)
    return render(request, "downloader/item.html", context={"item": item})


def completed(request):
    return render(request, "downloader/completed.html")
