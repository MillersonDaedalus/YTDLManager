from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponse, HttpResponseRedirect



# Create your views here.
def index(request):
    pass