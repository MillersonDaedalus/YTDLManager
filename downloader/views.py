from django.shortcuts import render
from django.http import HttpResponse

from .models import DownloadQueue, DownloadedFiles


# Create your views here.
def index(request):
    queue = DownloadQueue.objects.all()
    context = {
        "items_in_queue" : queue
    }
    #output = "There are ",str(len(queue))," downloads in the queue right now \n",", ".join(q.url for q in queue)
    return render(request, "downloader/index.html", context)


def requests(request, user):
    items = DownloadedFiles.objects.filter(user__exact=str(user))
    return render(request, "downloader/completed.html", context={"list_of_items": items, "user" : user})

def item(request, user, item_id):
    item = DownloadedFiles.objects.get(id__exact=item_id)
    return render(request, "downloader/item.html", context={"item": item})