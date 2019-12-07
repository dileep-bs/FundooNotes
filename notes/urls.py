from django.urls import path,include
# from .note import views
from . import views

urlpatterns=[
         path("uploadimage/",views.UploadMedia.as_view(), name='UploadImage'),
         path("notes/", views.NoteCreate.as_view(), name="notes"),
         path("note/<note_id>", views.NoteUpdate.as_view(), name="note_update"),
         path("label", views.LabelsCreate.as_view(), name="label_get"),
         path("label/<label_id>", views.LabelsUpdate.as_view(), name="label_update"),
         path("archive/",views.Archive.as_view(),name="archive"),
         path("trash/", views.Trash.as_view(), name="Trash"),
         path("reminder/",views.Remider.as_view(),name='Reminder'),

 ]