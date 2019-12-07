from rest_framework import serializers
from django.contrib.auth.models import User

from . models import Create_Notes


# class Create_NotesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Create_Notes
#         fields = ['user', 'title','note',]
#
# class NoteShareSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Create_Notes
#         fields = ['user','title', 'note']
#
#
