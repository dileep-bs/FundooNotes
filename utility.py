import jwt
# import settings
from django.conf import settings
from django.contrib.auth.models import User
from django_short_url.models import ShortURL
from django_short_url.views import get_surl


def smd_response(self, success, message, data):
    response = {"success": "", "message": "", "data": "", 'success': success, 'message': message, 'data': data}
    return response


class Response:

    def __init__(self):
        # Headers modification
        pass

    def json_response(self, json):
        # JSON Response
        pass


class Crypto:
    __algo = 'HS256'
    __secret = settings.SECRET_KEY

    def __init__(self, *args, **kwargs):
        self.__algo = 'HS256'
        self.__secret = settings.SECRET_KEY
        pass

    def encode_token(self, payload):
        jwt_token = {"token": jwt.encode(payload, self.__secret, self.__algo).decode('utf-8')}
        token = jwt_token['token']
        return token

    def decode_tok(self, token2):
        print("inside decode")
        tokenobj = ShortURL.objects.get(surl=token2)
        tokens = tokenobj.lurl
        print(tokens)
        user_details = jwt.decode(tokens, self.__secret, self.__algo)
        username = user_details['username']
        return username

    def short_url(self, key):
        url = str(key)
        surl = get_surl(url)
        short = surl.split("/")
        return short
