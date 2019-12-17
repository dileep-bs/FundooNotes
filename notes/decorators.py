import json
import logging
import jwt
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import HttpResponse, redirect, get_object_or_404
from fundoonotes.settings import file_handler
from notes.models import Label
from notes.lib.redis import RedisOperation

redisobject=RedisOperation()
redis=redisobject.red

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)



def redirect_after_login(function):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.id is not None:
            logger.info("you're already loggedin ")
            return redirect("/api/note")
        return function(request, *args, **kwargs)

    return wrapper


def login_decorator(function):
    def wrapper(request, *args, **kwargs):
        response = {"success": False, "message": "try again", 'data': []}
        try:
            if request.META["HTTP_AUTHORIZATION"]:
                try:
                    header = request.META["HTTP_AUTHORIZATION"]
                    token = header.split(" ")
                    decode = jwt.decode(token[1], settings.SECRET_KEY)
                    user = User.objects.get(id=decode['user_id'])
                    if redis.get(user.username) is None:
                        logger.error("user credential were not found in redis ")
                        response['message'] = "something went wrong please login back"
                        return HttpResponse(json.dumps(response, indent=2), status=404)
                    logger.info("%s logged in using simple jwt", user.username)
                    return function(request, *args, **kwargs)
                except jwt.exceptions.DecodeError as e:
                    response["message"] = str(e)
                    logger.error("token decode error")
                    return HttpResponse(json.dumps(response, indent=2), status=404)
                except jwt.exceptions.ExpiredSignatureError as e:
                    logger.error("token expired ")
                    response['message'] = str(e)
                    return HttpResponse(json.dumps(response, indent=2), status=404)
                except User.DoesNotExist as e:
                    logger.error("token decode user id doesnt exist")
                    response["message"] = str(e)
                    return HttpResponse(json.dumps(response, indent=2), status=404)
        except KeyError:
            pass

        if request.COOKIES.get(settings.SESSION_COOKIE_NAME) is None:
            logger.error("session_id not present or expired")
            response = {"success": False, "message":  "something went wrong please login again", 'data': []}
            return HttpResponse(json.dumps(response, indent=2), status=404)
        else:
            logger.info("%s logged in using social login ", request.user)
            return function(request, *args, **kwargs)

    return wrapper


def validate_collab_put(function):
    def wrapper(request, note_id):
        user = request.user
        try:
            label = request.data['label']

            if labelvalidator(label, user.id):
                smd = {'success': False, 'message': 'label is not created by this user or user does not exist',
                       'data': []}
                return HttpResponse(json.dumps(smd, indent=2), status=400)
        except KeyError:
            pass

        try:
            collaborators = request.data['collaborators']
            if collvalidator(collaborators):
                smd = {'success': False, 'message': 'email not vaild',
                       'data': []}
                return HttpResponse(json.dumps(smd, indent=2), status=400)
        except KeyError:
            pass
        return function(request, note_id)

    return wrapper


def labelvalidator(label, user_id):
    lab = []
    try:
        # pdb.set_trace()
        ll = Label.objects.filter(user_id=user_id)
        for i in range(len(label)):
            get_object_or_404(Label, name=label[i], user_id=user_id)
            lab.append(ll.values()[i]["name"])

        return False
    except Exception:
        logger.error("%s was not found under %s  ", label, user_id)
        return True


def collvalidator(collaborators):
    try:
        for email in collaborators:
            email_id = User.objects.filter(email=email)
            id = email_id.values()[0]['id']
        return False
    except Exception:
        logger.error(" %s does not exist", collaborators)
        return True