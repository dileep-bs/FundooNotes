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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from notes.serializer import UploadSerializer
# from notes.decorators import login_decorator
from notes.models import Notes
from notes.serializer import NotesSerializer
from fundoonotes.settings import file_handler
from notes.decorators import red
from notes.models import Label
from notes.serializer import LabelSerializer
from notes.serializer import UpdateSerializer

from .decorators import login_decorator
from .lib.s3_file import UploadImage
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


class UploadMedia(GenericAPIView):
    serializer_class = UploadSerializer

    def post(self, request):
        """Upload media files to s3 bucket object"""

        try:
            image = request.FILES.get('file')  # key
            print(image, "image")
            clsobj = UploadImage()  # creating obj for a aws cls
            print('obj creation for UploadImage')
            response = clsobj.upload_file(image)  # built method for upload media file
            print('after image')
            return HttpResponse(json.dumps(response))
        except Exception as e:
            print(e)
            response = self.smd_response(False, 'Upload unsuccessful', '')
            return HttpResponse(json.dumps(response))


@method_decorator(login_decorator, name='dispatch')
class NoteCreate(GenericAPIView):
    serializer_class = NotesSerializer

    def get(self, request):
        """Getting all the notes present in user database"""
        response = {'success': False, 'message': 'no notes', 'data': []}
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

        #     user = request.user
        #     redis_data = red.hvals(str(user.id) + "label")
        #     print(redis_data, 'redis datagklsfjgvkljsn')
        #     if len(redis_data) == 0:
        #         notes = Notes.objects.filter(user_id=user.id)
        #         Note_name = [i.note for i in notes]
        #         # print(labels,label_name,'hfgjnxcgnfnhfgnfh')
        #         logger.info("labels where taken from db for user")
        #         return Response(Note_name, status=200)
        #     logger.info("got notes ")
        #     return render(request, 'listofnotes.html', {'notes': notes}, status=200)
        # except Exception as e:
        #     logger.info("happen something while rendering notes")
        #     response = {'success': False, 'message': "bad response", 'data': []}
        #     return Response(response, status=400)

    def post(request):
        """creating and posting all the notes present in user database"""
        user = request.user
        try:
            data = request.data
            user = request.user
            collaborator_list = []  # empty collaborator list to id                                           #label input and col id
            data["label"] = [Label.objects.filter(user_id=user.id, name=name).values()[0]['id'] for name in
                             data["label"]]
            collaborator = data['collaborators']
            for email in collaborator:
                email_id = User.objects.filter(email=email)
                user_id = email_id.values()[0]['id']
                collaborator_list.append(user_id)
            data['collaborators'] = collaborator_list
            # print(data['collaborators'])            #prints collaborator who are all in db
            serializer = NotesSerializer(data=data, partial=True)
            if serializer.is_valid():
                note_create = serializer.save(user_id=user.id)
                response = {'success': True, 'message': "note created", 'data': []}
                if serializer.data['is_archive']:
                    red.hmset(str(user.id) + "is_archive",
                              {note_create.id: str(json.dumps(serializer.data))})  # created note is cached in redis
                    logger.info("note created %s and note id is %s", user, note_create.id)
                    return HttpResponse(json.dumps(response, indent=2), status=201)
                else:
                    if serializer.data['reminder']:
                        red.hmset("reminder", {note_create.id: str(json.dumps(
                            {"email": user.email, "user": str(user), "note_id": note_create.id,
                             "reminder": serializer.data["reminder"]}))})
                    red.hmset(str(user.id) + "note", {note_create.id: str(json.dumps(serializer.data))})
                    logger.info("note is created for %s with note data as %s", user, note_create)
                    return HttpResponse(json.dumps(response, indent=2), status=201)
            logger.error(" %s for  %s", user, serializer.errors)
            response = {'success': False, 'message': " note can't create", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=400)
        except Exception as e:
            print(e)
            print("error while creating label")
            logger.error("exception %s", str(e))
            response = {'success': False, 'message': "bas response", 'data': []}
            return Response(response, status=400)


@method_decorator(login_decorator, name='dispatch')
class NoteUpdate(GenericAPIView):
    serializer_class = UpdateSerializer

    def put(request, note_id):
        """Update Note attributes using pirticuler Note_ID"""
        user = request.user
        try:
            # pdb.set_trace()
            # data is fetched from user
            instance = Notes.objects.get(id=note_id)
            print(instance, 'note data')
            data = request.data
            if len(data) == 0:
                raise KeyError
            collaborator_list = []  # empty coll  list is formed where data is input is converted to id
            try:
                label = data["label"]
                data['label'] = [Label.objects.get(name=name, user_id=request.user.id).id for name in label]
            except KeyError:
                logger.debug('label was not added by the user %s', user)
                pass
            try:
                collaborator = data['collaborators']
                # for loop is used for the getting label input and coll input ids
                for email in collaborator:
                    emails = User.objects.filter(email=email)
                    user_id = emails.values()[0]['id']
                    collaborator_list.append(user_id)
                data['collaborators'] = collaborator_list
            except KeyError:
                logger.debug('collaborators was not added by the user %s', user)
                pass
            serializer = UpdateSerializer(instance, data=data, partial=True)
            # here serialized data checked for validation and saved
            if serializer.is_valid():
                note_create = serializer.save()
                response = {'success': True, 'message': "note updated", 'data': [serializer.data]}
                print(serializer.data)
                # pdb.set_trace()
                if serializer.data['is_archive']:
                    red.hmset(str(user.id) + "is_archive",
                              {note_create.id: str(json.dumps(serializer.data))})
                    logger.info("note was updated with note id :%s for user :%s ", note_id, user)
                    return HttpResponse(json.dumps(response, indent=2), status=200)
                elif serializer.data['is_trashed']:
                    red.hmset(str(user.id) + "is_trashed",
                              {note_create.id: str(json.dumps(serializer.data))})
                    logger.info("note was updated with note id :%s for user :%s ", note_id, user)
                    return HttpResponse(json.dumps(response, indent=2), status=200)
                else:
                    if serializer.data['reminder']:
                        red.hmset("reminder",
                                  {note_create.id: str(json.dumps({"email": user.email, "user": str(user),
                                                                   "note_id": note_create.id,
                                                                   "reminder": serializer.data["reminder"]}))})

                    red.hmset(str(user.id) + "note",
                              {note_create.id: str(json.dumps(serializer.data))})
                    logger.info("note was updated with note id :%s for user :%s ", note_id, user)
                    return HttpResponse(json.dumps(response, indent=2), status=200)
            logger.error("note was updated with note id :%s for user :%s ", note_id, user)
            response = {'success': False, 'message': "note was not created", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=400)
        except KeyError as e:
            print(e)
            logger.error("no data was provided from user %s to update", str(e), user)
            response = {'success': False, 'message': "note already upto data ", 'data': []}
            return Response(response, status=400)
        except Exception as e:
            logger.error("got error :%s for user :%s while updating note id :%s", str(e), user, note_id)
            response = {'success': False, 'message': str(e), 'data': []}
            return Response(response, status=404)

    def delete(self, request, note_id, *args, **kwargs):
        """Deleteing pirticuler note using Note_ID"""
        response = {'success': False, 'message': 'note not exist', 'data': []}
        user = request.user
        try:
            note = Notes.objects.get(id=note_id)
            note.is_trashed = True  # is_deleted, is_removed, is_trashed
            note.save()
            note_data = Notes.objects.filter(id=note_id)
            serialized_data = NotesSerializer(note_data, many=True)
            red.hmset(str(user.id) + "is_trashed", {note.id: str(json.dumps(serialized_data.data))})
            red.hdel(str(user.id) + "note", note_id)
            logger.info('note deleted')
            response = {'success': True, 'message': 'note deleted successfully', 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.info('something happend wrrong while delete note %s', str(e))
            # print(e)
            return Response(response, status=400)


@method_decorator(login_decorator, name='dispatch')
class LabelsCreate(GenericAPIView):
    serializer_class = LabelSerializer

    def get(self, request):
        """Getting all the labels present in user database"""
        response = {"success": False, "message": "invalid response", "data": []}
        user = request.user
        redis_data = red.hvals(str(user.id) + "label")
        print(redis_data, 'redis datagklsfjgvkljsn')
        if len(redis_data) == 0:
            labels = Label.objects.filter(user_id=user.id)
            label_name = [i.name for i in labels]
            # print(labels,label_name,'hfgjnxcgnfnhfgnfh')
            logger.info("labels where taken from db for user", )
            return Response(label_name, status=200)
        logger.info("got lables ")
        return Response(redis_data, status=200)

    def post(self, request):
        """creating and posting all the labels present in user database"""
        user = request.user
        response = {"success": False, "message": "invalid response", "data": []}
        label = request.data["name"]
        if Label.objects.filter(user_id=user.id, name=label).exists():
            logger.info('label is already exists for')
            response['message'] = "label name is already exists"
            return Response(response, status=400)
        else:
            label_created = Label.objects.create(user_id=user.id, name=label)
            red.hmset(str(user.id) + "label", {label_created.id: label})
            logger.info("label is created for %s", user)
            response = {"success": True, "message": "label is created", "data": label}
            return HttpResponse(json.dumps(response), status=201)


class LabelsUpdate(GenericAPIView):
    serializer_class = LabelSerializer

    def put(self, request, label_id):
        """Update Label using pirticuler Label_ID"""
        response = {"success": False, "message": "bad happened", "data": []}
        user = request.user
        try:
            print('inside label updatye')
            requestBody = json.loads(request.body)
            print(requestBody, 'adfess')
            label_name = requestBody['name']
            label_updated = Label.objects.get(id=label_id, user_id=user.id)
            print(label_updated, 'wrtgtestgestygres')
            label_updated.name = label_name
            label_updated.save()
            red.hmset(str(user.id) + "label", {label_updated.id: label_name})
            print(red.hmset, 'ertygestygestgsetyetyg')
            response["message"] = "label updated successfully"
            response["data"] = [label_name]
            response["success"] = True
            logger.info("label was updated for %s both on redis and database ", user)
            return HttpResponse(json.dumps(response, indent=2), status=200)
        except Exception as e:
            logger.error("error:%s while creating label for %s", str(e), user)
            return Response(response, status=404)

    def delete(self, request, label_id):
        """Deleteing pirticuler label using Label_ID"""
        response = {"success": False, "message": "label does not exist ", "data": []}
        user = request.user
        try:
            red.hdel(str(user.id) + "label", label_id)
            label_id = Label.objects.get(id=label_id, user_id=user.id)
            label_id.delete()
            logger.info("label is deleted for %s", user)
            response = {"success": True, "message": "label is deleted", "data": []}
            return Response(response, status=204)
        except Exception as e:
            logger.info("got error : %s while deleting label for  %s", str(e), user)
            return Response(response, status=404)


class Archive(GenericAPIView):
    def get(self, request):
        """Getting all the Archived notes present in user database"""
        response = {"success": False, "message": "bad response", "data": []}
        user = request.user
        redis_data = red.hvals(str(user.id) + "is_archive")
        try:
            if len(redis_data) == 0:
                response = {"success": True, "message": "archived notes are here", "data": []}
                no = Notes.objects.filter(user_id=user.id, is_archive=True)
                if len(no) == 0:
                    logger.info("zero archived notes fetched for %s", user)
                    return HttpResponse(json.dumps(response), status=200)
                else:
                    logger.info("archive data is loaded from database for %s", user)
                    return HttpResponse(no.values(), status=200)
            logger.info("archive data is loaded from redis for %s", user)
            return HttpResponse(redis_data, status=200)
        except Exception as e:
            logger.error(" %e", str(e))
            return HttpResponse(json.dumps(response), status=404)


class Trash(GenericAPIView):
    def get(self, request):
        """Getting all the Deleted notes present in user database"""
        response = {"success": False, "message": "bad response", "data": []}
        user = request.user
        # pdb.set_trace()
        try:
            redis_data = red.hvals(str(user.id) + "is_trashed")
            if len(redis_data) == 0:
                user = request.user
                no = Notes.objects.filter(user_id=user.id, is_trashed=True)
                if len(no) == 0:
                    logger.info("No notes in Trash for %s", user)
                    response = {"success": True, "message": "No notes in Trash "}
                    return HttpResponse(json.dumps(response), status=200)
                logger.info("Trash data is loaded for %s from database", user)
                return HttpResponse(no.values())
            logger.info("Trash data is loaded for %s from redis", user)
            return HttpResponse(redis_data)
        except Exception as e:
            logger.error("error:%e for %s while fetching trashed notes", user, str(e))
            HttpResponse(json.dumps(response, status=404))


class Remider(GenericAPIView):
    def get(self, request):
        """Getting all the Redminded notes present in user database"""
        response = {"success": False, "message": "bad response", "data": []}
        try:
            user = request.user
            print(user)
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
            self.response['message'] = 'exception came'
            logger.info("Reminder unsuccessfull")
            return HttpResponse(json.dumps(self.response))


class Celery(GenericAPIView):
    serializer_class = NotesSerializer

    def get(self, request):
        """Reminder Email"""
        response = {"success": False, "message": "bad response", "data": []}

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
                    from_email = EMAIL_HOST_USER
                    to = 'dileep.bs@yahoo.com'
                    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
                    response = {"success": True, "message": "mail successfully sent!.........", "data": []}
                    logger.info("email sent %s ", request.user)
            return HttpResponse('successs')
        except Exception as e:
            logger.info("exception %s" ,str(e))
            return HttpResponse(json.dumps(self.response))
