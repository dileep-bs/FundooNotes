import jwt
import requests
from fundoo.fundoo.settings import SECRET_KEY, AUTH_ENDPOINT

class Token_gen:
    def token_activation(username, password):
        data = {
            'username': username,
            'password': password,
        }
        token = jwt.encode(data, SECRET_KEY, algorithm="HS256").decode('utf-8')
        return token


    def token_validation(username, password):

        data = {
            'username': username,
            'password': password
        }
        tokson = requests.post(AUTH_ENDPOINT, data=data)
        token = tokson.json()['key']
        return token