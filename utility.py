import jwt
from django.conf import settings
from django_short_url.models import ShortURL
from django_short_url.views import get_surl


class Response:
    def __init__(self,  __success="success", __message="message",__data="data"):
            self.__success = __success
            self.__message = __message
            self.__data = __data

    def jsonResponse(self, success, message,data):
        if success:
            smd={self.__success : success, self.__message: message, self.__data : data}
            return smd
        else:
            smd= {self.__success: success, self.__message: message, self.__data: data}
            return smd


class Crypto:
    def __init__(self, *args, **kwargs):
        self.__algo = 'HS256'
        self.__secret = settings.SECRET_KEY
        pass

    def encode_token(self, payload):
        jwt_token = {"token": jwt.encode(payload, self.__secret, self.__algo).decode('utf-8')}
        token = jwt_token['token']
        return token

    def decode_tok(self, token2):
        tokenobj = ShortURL.objects.get(surl=token2)
        tokens = tokenobj.lurl
        user_details = jwt.decode(tokens, self.__secret, self.__algo)
        username = user_details['username']
        return username

    def short_url(self, key):
        url = str(key)
        surl = get_surl(url)
        short = surl.split("/")
        return short
