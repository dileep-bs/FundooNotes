import json
import logging
import jwt
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from rest_framework.generics import GenericAPIView
from .serialized import LoginSerializer, ResetSerializer, UserSerializer, ForgotSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from fundoonotes.settings import file_handler
from utility import Crypto
obj=Crypto()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

class login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        """
        param APIView: user request is made from the user
        return: will check the credentials and will user
        """
        try:
            username = request.data['username']
            password = request.data['password']
            smd = {'success': False, 'message': "login Failed", 'data': []}
            payload = {'username': username}
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                obj.encode_token(payload)
                smd = {'success': True, 'message': "login successful", 'data': [], }
                return HttpResponse(json.dumps(smd), status=201)
            else:
                smd['message'] = 'Check your password and username'
                return HttpResponse(json.dumps(smd), status=400)
        except Exception as e:
            logger.error(str(e))
            smd = {'success': False, 'message': "something went wrong", 'data': []}
            return HttpResponse(json.dumps(smd))


class register(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        """
            param request: request is made after filling the form
            return: will send him the JWT token for validation
        """
        try:
            username = request.data['username']
            password = request.data['password']
            email = request.data['email']
            smd = {'success': False, 'message': "reg failed", 'data': []}
            if User.objects.filter(email=email).exists():
                smd['message'] = 'Email is already registered'
                return HttpResponse(json.dumps(smd), status=400)
            try:
                user = User.objects.create_user(username=username, password=password, email=email, is_active=False)
                assert isinstance(user, object)
                payload = {'username': user.username, 'email': user.email}
                key = obj.encode_token(payload)
                short =obj.short_url(key)
                mail_subject = 'Link to activate the account'
                mail_message = render_to_string('activate.html',
                                                {'user': user.username,
                                                 'domain': get_current_site(request).domain,
                                                 'token': short[2],})
                recipient_email = [EMAIL_HOST_USER]
                email = EmailMessage(mail_subject, mail_message, to=[recipient_email])
                email.send()
                smd = {'success': False, 'message': "Check your mail for activate", 'data': [key]}
                return HttpResponse(json.dumps(smd), status=201)
            except Exception:
                smd["message"] = "username already taken"
                return HttpResponse(json.dumps(smd), status=400)
        except Exception as e:
            smd["message"] = str(e)
            return HttpResponse(json.dumps(smd), status=400)


def activate(request, token):
    try:
        tokenobj = ShortURL.objects.get(surl=token)
        token = tokenobj.lurl
        user_details = jwt.decode(token, 'secret', algorithms='HS256')
        user_name = user_details['username']
        try:
            user = User.objects.get(username=user_name)
        except ObjectDoesNotExist as e:
            print(e)
        if user is not None:
            user.is_active = True
            user.save()
            messages.info(request, "account is active now")
            return redirect('/login')
        else:
            return redirect('register')
    except KeyError:
        messages.info(request, 'mail sending failed')
        return redirect('/register')


class sendmail(GenericAPIView):
    serializer_class = ForgotSerializer

    def post(self, request):
        """
        :param request:
        ------------
                    request is made for resetting password
        :return:
        -----------
                    will return email where password reset link will be attached
        """
        emailid = request.data["email"]
        print(emailid)
        smd = {'success': False, 'message': "not a vaild email ", 'data': []}
        try:
            user = User.objects.get(email=emailid)
            print(user)
            if user is not None:
                payload = {'username': user.username,
                           'email': user.email}
                key = obj.encode_token(payload)
                short=obj.short_url(key)
                mail_subject = "Reset your password by clicking below link"
                mail_message = render_to_string('verify.html', {'user': user.username,
                                                                'domain': get_current_site(request).domain,
                                                                'token': short[2]})
                send_mail(mail_subject, mail_message, EMAIL_HOST_USER, [emailid])
                smd = {'success': True, 'message': "check your mail for reset", 'data': []}
                return HttpResponse(json.dumps(smd), status=201)
        except Exception as e:
            print(e)
            smd["success"] = False
            smd['message'] = "email doesn't exist"
            return HttpResponse(json.dumps(smd), status=400)


def activate(request, tkn):
    """
        :param request: request is made by the used
        :param token:  token is fetched from url
        :return: will register the account
    """
    try:
        username = obj.decode_tok(tkn)
        user = User.objects.get(username=username)
        if user is not None:
            user.is_active = True
            user.save()
            messages.info(request, "your account is actived")
            return redirect('/login')
        else:
            return redirect('register')
    except KeyError:
        messages.info(request, 'mail sending failed')
        return redirect('/register')


def verify(request, token1):
    try:
        username=obj.decode_tok(token1)
        user = User.objects.get(username=username)
        if user is not None:
            # return redirect(reversed('resetmail' + str(token1) + '/'))
            return HttpResponseRedirect(reverse('url_name'))
            # return redirect('/api/resetpassword/' + str(token1) + '/') # Reverse URL
        else:
            messages.info("Invalid user")
            return redirect('register')
    except Exception as e:
        print(str(e))
        return redirect('resetmail')


class resetpassword(GenericAPIView):
    serializer_class = ResetSerializer

    def post(self, request, tok):
        """
        :param surl:  token is again send to the user
        :param request:  user will request for resetting password
        :return: will reset the password
        """
        smd = {"success": False, "message": "not a vaild user", "data": []}
        if request.method == 'POST':
            try:
                password = request.data['password']
                if len(password) < 4 or password == ' ':
                    smd["message"] = "Password should more than 4 digits"
                    logger.info("Password condition failed")
                    return HttpResponse(json.dumps(smd), status=200)
                else:
                    username = obj.decode_tok(tok)
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.save()
                    messages.info(request, "password reset successfully")
                    return redirect("login")
            except ObjectDoesNotExist as e:
                smd = {"success": False, "message": "somethong went wrong", "data": []}
                logger.info("user not found",str(e))


class logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request):
        """
        param request: logout request is made
        """
        smd = {"success": False, "message": "not a vaild user", "data": []}
        try:
            user = request.user
            smd = {"success": True, "message": "logged out", "data": []}
            return HttpResponse(json.dumps(smd), status=200)
        except Exception:
            return HttpResponse(json.dumps(smd), status=400)


class SendEmail(GenericAPIView):
    serializer_class = ForgotSerializer

    def post(self, request):
        """
            :param request: request is made for reset template password
            :return:  will return email where password reset template will be attached
        """
        smd = {"success": False, "message": "Email sending fail", "data": []}
        emailid = request.data["email"]
        user1 = request.user
        print(user1)
        try:
            user = User.objects.get(email=emailid)
            print(user)
            if user is not None:
                payload = {
                    'username': user.username,
                    'email': user.email
                }
                key = obj.encode_token(payload)
                short = obj.short_url(key)
                mail_subject = "Reset your password by clicking below link"
                mail_message = render_to_string(
                    'new.html', {
                        'user': user.username,
                        'domain': get_current_site(request).domain,
                        'user_token': short[2]
                    }
                )
                tepm = strip_tags(mail_message)
                msg = EmailMultiAlternatives(mail_subject, tepm, emailid, [emailid])
                msg.attach_alternative(mail_message, "text/html")
                msg.send()
                response_result = {
                    'success': True,
                    'message': "check your mail for reset",
                    'data': []
                }
                return HttpResponse(json.dumps(response_result), status=201)
        except Exception:
            smd = {"success": False, "message": "Inavalid user or Email id", "data": []}
            return HttpResponse(json.dumps(smd), status=400)
