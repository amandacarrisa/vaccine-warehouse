from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime
import json

# 7c - create
def create(request):
    if (request.session["role"] == "Supplier"):
        if (request.method == 'POST'):
            return createRSP(request)
        else:
            return getRSP(request)

# 7c - create to get auto filled data
def getRSP(request):
    context = {}

    

    
# 7c - create to do alter
def createRSP(request):
    context = {}