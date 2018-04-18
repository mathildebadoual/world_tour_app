# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from .utils import *

# Create your views here.
def index(request):
    ncou = int(request.GET['ncou'])
    ncon = int(request.GET['ncon'])
    budget = int(request.GET['budget'])
    duration = int(request.GET['duration'])
    origin = request.GET['origin']
    #list_airports = choose_countries(origin,ncou,ncon)
    #matrix = find_best_travel(list_airports,duration,ncou)
    a = 1
    return HttpResponse(a)
