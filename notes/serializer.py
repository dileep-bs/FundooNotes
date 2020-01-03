from rest_framework import serializers
from .models import Media
from rest_framework import serializers
from .models import Notes, Label
from rest_framework import serializers
from .models import Notes, Label


class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['file']


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'label', 'url','collaborators']


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note']


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name']


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'label', 'url','collaborators']


class NoteDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title']  # ,'note','label','reminder']
