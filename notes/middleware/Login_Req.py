import json
import logging
import jwt
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import HttpResponse, redirect, get_object_or_404
from fundoonotes.settings import file_handler
from notes.models import Label
from notes.lib.redis import RedisOperation
from rest_framework import status
from rest_framework_jwt.settings import api_settings

from fundoonotes.utility import Response

redisobject=RedisOperation()
redis=redisobject.red

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

obj1=Response()

class LogMiddle(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = request.path
        current_url = url.split("/")[1]
        if current_url == "api":
            try:
                token = request.META['HTTP_AUTHORIZATION']
                jwt_decode_handler = api_settings.SECRET_KEY
                new_token = str(token).split("Bearer ")[1]
                encoded_token = jwt_decode_handler(new_token)
                username = encoded_token['username']
                user = User.objects.get(username=username)
                if user and user.is_active:
                    pass
            except User.DoesNotExist:
                    res = obj1.jsonRespone(False, 'Authentication Required', '')
                    return HttpResponse(json.dumps(res), status=status.HTTP_400_BAD_REQUEST)
            except KeyError:
                if request.session:
                    user = request.user
                    if user.is_authenticated:
                        pass
                    else:
                        res = obj1.jsonRespone(False, 'Users credential not provided', '')
                        return HttpResponse(json.dumps(res), status=status.HTTP_400_BAD_REQUEST)
                else:
                    res = obj1.jsonRespone(False, 'Users credential not provided', '')
                    return HttpResponse(json.dumps(res), status=status.HTTP_400_BAD_REQUEST)
        else:
            return self.get_response(request)
