import json

# from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

# from .models import Create_Notes
from .serialized import Create_NotesSerializer, NoteShareSerializer


# from . import models

def index(request):
    return render(request, 'socialhome.html')

def page(request):
    return render(request, 'page.html')


class NoteShare(GenericAPIView):

    serializer_class = NoteShareSerializer

    def post(self, request):
        title = request.data['title']
        note = request.data['note']
        if title == "" or note == "":
            response = self.smd_response(False, 'Please fill the fields', '')
            return HttpResponse(json.dumps(response))
        return render(request, 'login.html', {'title': title, 'note': note})