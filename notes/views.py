import json
import logging
from datetime import timedelta
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from notes.serializer import UploadSerializer
from notes.models import Notes
from notes.serializer import NotesSerializer
from fundoonotes.settings import file_handler
from notes.decorators import redis
from notes.models import Label
from notes.serializer import LabelSerializer
from notes.serializer import UpdateSerializer
from .decorators import login_decorator
from .documents import Document
from .lib.s3_file import UploadImage
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .serializer import NoteDocSerializer
from fundoonotes.settings import MY_MAIL
from utility import Response
from .lib.redis import RedisOperation
red=RedisOperation()

obj1=Response()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


class UploadMedia(GenericAPIView):
    serializer_class = UploadSerializer

    def post(self, request):
        """Upload media files to s3 bucket object"""

        try:
            image = request.FILES.get('file')
            clsobj = UploadImage()
            response = clsobj.upload_file(image)
            return HttpResponse(json.dumps(response))
        except Exception as e:
            print(e)
            response = obj1.jsonResponse(False, 'Upload Unsuccessfull', '')
            return HttpResponse(json.dumps(response))


@method_decorator(login_decorator, name='dispatch')
class NoteData(GenericAPIView):
    serializer_class = NotesSerializer

    def post(self, request):
        """
             :Summary:
             ---------
                 New note will be create by the User.
             :Exception:
             ------------
                 KeyError: object

             :Returns:
             ---------
                 response: SMD format of note create message or with error message
        """
        user = request.user
        try:
            data = request.data
            if len(data) == 0:
                raise KeyError
            user = request.user
            collaborator_list = []
            data["label"] = [Label.objects.filter(user_id=user.id, name=name).values()[0]['id'] for name in data["label"]]
            collaborator = data['collaborators']
            for email in collaborator:
                email_id = User.objects.filter(email=email)
                user_id = email_id.values()[0]['id']
                collaborator_list.append(user_id)
            data['collaborators'] = collaborator_list
            serializer = NotesSerializer(data=data, partial=True)
            if serializer.is_valid():
                note_create = serializer.save(user_id=user.id)
                response = {'success': True, 'message': "note created", 'data': []}
                if serializer.data['is_archive']:
                    red.hmset(str(user.id) + "is_archive",
                              {note_create.id: str(json.dumps(serializer.data))})  # created note is cached in redis
                    logger.info("note is created for %s with note id as %s", user, note_create.id)
                    return HttpResponse(json.dumps(response, indent=2), status=201)
                else:
                    if serializer.data['reminder']:
                        red.hmset("reminder",  {note_create.id: str(json.dumps({"email": user.email, "user": str(user), "note_id": note_create.id,
                                                                   "reminder": serializer.data["reminder"]}))})
                    red.hmset(str(user.id) + "note", {note_create.id: str(json.dumps(serializer.data))})
                    logger.info("note is created for %s with note data as %s", user, note_create.__repr__())
                    return HttpResponse(json.dumps(response, indent=2), status=201)
            logger.error(" %s for  %s", user, serializer.errors)
            response = {'success': False, 'message': "note was not created", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=400)
        except KeyError as e:
            print(e)
            logger.error("got %s error for creating note as no data was provided for user %s", str(e), user)
            response = {'success': False, 'message': "one of the field is empty ", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=400)
        except Exception as e:
            print(e)
            logger.error("got %s error for creating note for user %s", str(e), user)
            response = {'success': False, 'message': "something went wrong", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=400)

    def get(self, request):
        """
        :Summary:
        ----------
            Note class will let authorized user to create and get notes.
        :Methods:
        ---------
            get: User will get all the notes.
            """
        notes_list = Notes.objects.all()
        page = request.GET.get('page')
        paginator = Paginator(notes_list, 1)
        user = request.user
        try:
            notes = paginator.page(page)
        except PageNotAnInteger:
            logger.warning("got %s error for getting note for user %s", str(PageNotAnInteger), user.username)
            notes = paginator.page(1)
        except EmptyPage:
            logger.warning("got %s error for getting note for user %s", EmptyPage, user)
            notes = paginator.page(paginator.num_pages)
        logger.info("all the notes are rendered to html page for user %s", user)
        return render(request, 'listofnotes.html', {'notes': notes}, status=200)


# @method_decorator(login_decorator, name='dispatch')
class NoteUpdate(GenericAPIView):
    serializer_class = UpdateSerializer

    def put(self,request, note_id):
        """
        :Summary:
        --------
             Update Note attributes using pirticuler Note_ID
        :Methods:
        ---------
            put: User will able to update existing note.
            delete: User will able to delete  note.

        """
        user = request.user
        try:
            instance = Notes.objects.get(id=note_id)
            data = request.data
            collaborator_list = []
            label = data["label"]
            data['label'] = [Label.objects.get(name=name, user_id=request.user.id).id for name in label]
            collaborator = data['collaborators']
            for email in collaborator:
                emails = User.objects.filter(email=email)
                user_id = emails.values()[0]['id']
                collaborator_list.append(user_id)
            data['collaborators'] = collaborator_list
            serializer = UpdateSerializer(instance, data=data, partial=True)
            serializer.save()
            res = obj1.jsonResponse(True, 'note updated', [serializer.data])
            return HttpResponse(json.dumps(res,indent=2),status=200)
        except KeyError as e:
            logger.error("no data was provided from user %s to update", str(e), user)
            res = obj1.jsonResponse(False, 'note already upto data ', '')
            return HttpResponse(json.dumps(res, indent=2), status=400)
        except Exception as e:
            logger.error("got error :%s for user :%s while updating note id :%s", str(e), user, note_id)
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return HttpResponse(json.dumps(res, indent=2), status=400)

    def delete(self, request, note_id, *args, **kwargs):
        '''
            :Summary:
            --------
                note will be deleted by the User.
            :Exception:
            -----------
                Exception:  if anything goes wrong.
            :Returns:
            ------------
                response:  User will able to delete note or error msg if something goes wrong
        '''
        user = request.user
        try:
            note = Notes.objects.get(id=note_id)
            note.is_trashed = True
            note.save()
            note_data = Notes.objects.filter(id=note_id)
            serialized_data = NotesSerializer(note_data, many=True)
            redis.hmset(str(user.id) + "is_trashed", {note.id: str(json.dumps(serialized_data.data))})
            redis.hdel(str(user.id) + "note", note_id)
            logger.info('note deleted')
            res = obj1.jsonResponse(True, 'note deleted successfully','')
            return HttpResponse(json.dumps(res, indent=2), status=200)
        except Exception:
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            logger.info('something happend wrrong while delete note %s')
            return Response(res, status=400)


@method_decorator(login_decorator, name='dispatch')
class LabelsCreate(GenericAPIView):
    serializer_class = LabelSerializer

    def get(self, request):
        """Getting all the labels present in user database
        :Summary:
        ---------
             Label create class will let authorized user to get and create label.
        :Methods:
        ---------
            get: User will get all the created labels by the  user.
            post: User will able to create more labels.
        """
        user = request.user
        redis_data = redis.hvals(str(user.id) + "label")
        if len(redis_data) == 0:
            labels = Label.objects.filter(user_id=user.id)
            label_name = [i.name for i in labels]
            logger.info("labels where taken from db for user", )
            return Response(label_name, status=200)
        logger.info("got lables for the user")
        return Response(redis_data, status=200)

    def post(self, request):
        """
            :Summary:
            ---------
                label will be create by the User.
            :Exception:
            ----------
                Exception:  if anything goes wrong.
            :Method:
            ----------
                 post: User will able to create more labels.
        """
        user = request.user
        label = request.data["name"]
        try:
            if Label.objects.filter(user_id=user.id, name=label).exists():
                logger.info('label is already exists for')
                res = obj1.jsonResponse(False, 'label name is already exists', '')
                return Response(res, status=400)
            else:
                label_created = Label.objects.create(user_id=user.id, name=label)
                redis.hmset(str(user.id) + "label", {label_created.id: label})
                logger.info("label is created for %s", user)
                res = obj1.jsonResponse(True, 'label Created', '')
                return HttpResponse(json.dumps(res), status=201)
        except Exception:
            logger.info("got an Exception for create label")
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return res


@method_decorator(login_decorator, name='dispatch')
class LabelsUpdate(GenericAPIView):
    serializer_class = LabelSerializer

    def put(self, request, label_id):
        """
        :Summary:
        ---------
            Update Label using pirticuler Label_ID
         :Methods:
         -------
           put: User will be able to update all notes.
        """
        user = request.user
        try:
            request_Body = json.loads(request.body)
            label_name = request_Body['name']
            label_updated = Label.objects.get(id=label_id, user_id=user.id)
            label_updated.name = label_name
            label_updated.save()
            redis.hmset(str(user.id) + "label", {label_updated.id: label_name})
            res = obj1.jsonResponse(True, 'label updated successfully',[label_name])
            logger.info("label was updated for %s both on redis and database ", user)
            return HttpResponse(json.dumps(res, indent=2), status=200)
        except Exception as e:
            logger.error("error:%s while creating label for %s", str(e), user)
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return res

    def delete(self, request, label_id):
        """
        :Summary:
        ---------
              Deleteing pirticuler label using Label_ID
        :Exception:
        ----------
              Exception object
        :Returns:
        ---------
              response: will return SMD format of deleted Label
        """
        user = request.user
        try:
            redis.hdel(str(user.id) + "label", label_id)
            label_id = Label.objects.get(id=label_id, user_id=user.id)
            label_id.delete()
            logger.info("label is deleted for %s", user)
            res = obj1.jsonResponse(True, 'label is deleted', '')
            return HttpResponse(json.dumps(res), status=200)
        except Exception as e:
            logger.info("got error : %s while deleting label for  %s", str(e), user)
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return Response(res, status=404)


@method_decorator(login_decorator, name='dispatch')
class Archive(GenericAPIView):
    def get(self, request):
        """
        :Summary:
        ---------
            Archive class will let authorized user to get archive notes.
        :Methods:
        ---------
            get: User will be able to get all archive notes.
        """
        user = request.user
        redis_data = redis.hvals(str(user.id) + "is_archive")
        try:
            if len(redis_data) == 0:
                no = Notes.objects.filter(user_id=user.id, is_archive=True)
                if len(no) == 0:
                    logger.info("zero archived notes fetched for %s", user)
                    res = obj1.jsonResponse(True, 'archived notes ', '')
                    return HttpResponse(json.dumps(res), status=200)
                else:
                    logger.info("archive data is loaded from database for %s", user)
                    return HttpResponse(no.values(), status=200)
            logger.info("archive data is loaded from redis for %s", user)
            return HttpResponse(redis_data, status=200)
        except Exception as e:
            logger.error("archived notes exception for user ", str(e))
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return HttpResponse(json.dumps(res), status=404)


class Trash(GenericAPIView):
    def get(self, request):
        """
        :Summary:
        ----------
            Getting all the Deleted notes present in user database
        :Methods:
        ---------
            get: User will be able to get all trashed notes.
        """
        user = request.user
        try:
            redis_data = redis.hvals(str(user.id) + "is_trashed")
            if len(redis_data) == 0:
                user = request.user
                no = Notes.objects.filter(user_id=user.id, is_trashed=True)
                if len(no) == 0:
                    logger.info("No notes in Trash for %s", user)
                    res = obj1.jsonResponse(True, 'No notes in Trash ', '')
                    return HttpResponse(json.dumps(res), status=200)
                logger.info("Trash data is loaded for %s from database", user)
                return HttpResponse(no.values())
            logger.info("Trash data is loaded for %s from redis", user)
            return HttpResponse(redis_data)
        except Exception as e:
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            logger.error("error for while fetching trashed notes")
            return HttpResponse(json.dumps(res, status=404))


class Remider(GenericAPIView):
    def get(self, request):
        """
        :Summary:
        ----------
            Getting all the Redminded notes present in user database
        :Methods:
        ----------
            get: User will be able to get all reminder notes with fired and upcoming reminder.
                for upcoming reminder email will be set to user email address.
        """
        try:
            user = request.user
            user_id = user.id
            note_obj = Notes.objects.filter(user_id=user_id)
            reminderlist = []
            completedlist = []
            for i in range(len(note_obj.values())):
                if note_obj.values()[i]['reminder'] is None:
                    continue
                elif timezone.now() > note_obj.values()[i]['reminder']:
                    completedlist.append(note_obj.values()[i])
                else:
                    reminderlist.append(note_obj.values()[i])
            remid = {
                'reminder': reminderlist,
                'compl': completedlist
            }
            remdstr = str(remid)
            logger.info("Reminders data is loaded for %s", user)
            return HttpResponse(note_obj.values(), status=200)
        except Notes.DoesNotExist:
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            logger.info("Reminder unsuccessfull...")
            return HttpResponse(json.dumps(res))


class Celery(GenericAPIView):
    serializer_class = NotesSerializer

    def get(self, request):
        """
        :Summary:
        ---------
            Celery class works on clery beat and every 1 min this end point is hit.
        :Methods:
        ---------
            get: this method where logic is written for triggering reminders notification service where
               email is sent if reminder time matched with current time.
        """
        reminder = Notes.objects.filter(reminder__isnull=False)
        start = timezone.now()
        end = timezone.now() + timedelta(minutes=1)
        try:
            for i in range(len(reminder)):
                if start < reminder.values()[i]["reminder"] < end:
                    user_id = reminder.values()[i]['user_id']
                    user = User.objects.get(id=user_id)
                    subject = 'Reminder Note'
                    html_message = render_to_string('mailfrom.html', {'context': 'values'})
                    plain_message = strip_tags(html_message)
                    mail.send_mail(subject, plain_message, EMAIL_HOST_USER, [MY_MAIL], html_message=html_message)
                    res = obj1.jsonResponse(True, 'mail successfully sent!.........', '')
                    logger.info("email sent %s ", request.user)
            return HttpResponse(json.dumps((res), status=200))
        except Exception as e:
            logger.info("exception %s", str(e))
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return HttpResponse(json.dumps(res))


class Searchnotes(GenericAPIView):
    serializer_class = NoteDocSerializer

    def post(self, request):
        """Elastic search for a notes,title..etc"""
        user=request.user
        try:
            word = request.data['title']
            findresult = Document.search().query({
                "bool": {
                    "must": [
                        {"multi_match": {
                            "query": word,
                            "fields": ['title']
                        }},
                    ],
                    "filter": [
                        {"term": {"user.username": str(request.user)}}
                    ]
                }
            })
            result = NotesSerializer(findresult.to_queryset(), many=True)
            return HttpResponse(json.dumps(result.data, indent=2), status=200)
        except Exception:
            logger.error("Couldn't make search operation for user %s  ",user)
            res = obj1.jsonResponse(False, 'Something went wrong ', '')
            return HttpResponse(json.dumps(res,indent=2), status=400)
