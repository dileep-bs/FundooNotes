import json
import logging

import requests
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from .serializer import LoginSerializer, ResetSerializer, UserSerializer, ForgotSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from fundoonotes.settings import file_handler, AUTH_ENDPOINT
from utility import Crypto
from utility import Response



obj = Crypto()
obj1 = Response()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


class Login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        """
        :param APIView:
        --------------
                user request is made from the user
        :return:
        --------
                will check the credentials and will user
        """
        try:
            username = request.data['username']
            password = request.data['password']
            payload = {'username': username}
            user = auth.authenticate(username=username, password=password)
            print(user)
            if user is not None:
                login_token=requests.post(AUTH_ENDPOINT,data=payload)
                res = obj1.jsonResponse(True, 'Login success',login_token)
                return HttpResponse(json.dumps(res), status=200)
            else:
                res = obj1.jsonResponse(False, 'Check your password and username','')
                return HttpResponse(json.dumps(res), status=400)
        except Exception as e:
            res = obj1.jsonResponse(False, 'something went wrong', '')
            logger.error(str(e))
            return HttpResponse(json.dumps(res))


class Register(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        """
            :param request:
             -------------
                        request is made after filling the form
            :return:
            ------------
                        will send him the JWT token for validation
        """
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']
        try:
            if username == "" or email == "" or password == "":
                res = obj1.jsonResponse(False, '"one of the details missing"','')
                logger.error("one of the details missing logging in")
                return HttpResponse(json.dumps(res), status=400)
            elif User.objects.filter(email=email).exists():
                res = obj1.jsonResponse(False, 'email address is already registered','')
                logger.error("email address is already registered  while logging in")
                return HttpResponse(json.dumps(res), status=400)
            elif User.objects.filter(username=username).exists():
                res = obj1.jsonResponse(False, 'username is already registered','')
                logger.error("username is already registered")
                return HttpResponse(json.dumps(res), status=400)
            else:
                user = User.objects.create_user(username=username,
                                                email=email,
                                                password=password,
                                                is_active=True)
                user.save()
                if user is not None:
                    payload = {'username': user.username,
                               'email': user.email
                               }
                    key = obj.encode_token(payload)
                    short = obj.short_url(key)
                    mail_subject = "Activate your account by clicking below link"
                    mail_message = render_to_string('activate.html', {
                        'user': user.username,
                        'domain': get_current_site(request).domain,
                        'u_token': short[2]
                    })
                    send_mail(mail_subject, mail_message, EMAIL_HOST_USER, [email])
                    res = obj1.jsonResponse(True, 'please check the mail and click on the link  for validation', '')
                    return HttpResponse(json.dumps(res), status=200)
        except ValueError as e:
            res = obj1.jsonResponse(False, 'user data not sufficient', '')
            return HttpResponse(json.dumps(res), status=400)
        except Exception as e:
            res = obj1.jsonResponse(False, 'something went wrong', '')
            logger.error("error: %s while loging in ", str(e))
            return HttpResponse(json.dumps(res), status=400)


class Sendmail(GenericAPIView):
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
        try:
            user = User.objects.get(email=emailid)
            if user is not None:
                payload = {'username': user.username,
                           'email': user.email}
                key = obj.encode_token(payload)
                short = obj.short_url(key)
                mail_subject = "Reset your password by clicking below link"
                mail_message = render_to_string('verify.html', {'user': user.username,
                                                                'domain': get_current_site(request).domain,
                                                                'u_token': short[2]}, )
                send_mail(mail_subject, mail_message, EMAIL_HOST_USER, [emailid])
                res = obj1.jsonResponse(True, 'check your mail for reset', '')
                return HttpResponse(json.dumps(res), status=201)
        except Exception:
            res = obj1.jsonResponse(False, 'Something went wrong', '')
            return HttpResponse(json.dumps(res), status=400)


def activate(request, token2):
    try:
        username = obj.decode_tok(token2)
        user = User.objects.get(username=username)
        if user is not None:
            user.is_active = True
            user.save()
            logger.info(request, "your account is activated")
            return redirect('login')
        else:
            return redirect('register')
    except KeyError:
        messages.info(request, 'Email sending failed')
        return redirect('register')


def verify(request, token1):
    try:
        username = obj.decode_tok(token1)
        user = User.objects.get(username=username)
        if user is not None:
            return redirect(reverse('resetpassword', args=[token1]))
        else:
            logger.info("Invalid user")
            return redirect('register')
    except Exception as e:
        logger.info("User credential missing", str(e))
        return redirect('resetpassword')


class resetpassword(GenericAPIView):
    serializer_class = ResetSerializer

    def post(self, request, token1):
        """
        :param surl:
        ------------
                    token is again send to the user
        :param request:
        ------------
                    user will request for resetting password
        :return:
        ------------
                    will reset the password
        """
        if request.method == 'POST':
            try:
                password = request.data['password']
                if len(password) < 4 or password == ' ':
                    res = obj1.jsonResponse(False, 'Password should more than 4 digits', '')
                    logger.info("Password condition failed")
                    return HttpResponse(json.dumps(res), status=200)
                else:
                    username = obj.decode_tok(token1)
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.save()
                    return redirect("login")
            except Exception as e:
                res = obj1.jsonResponse(False,'Something went wrong', '')
                logger.info("Coudnt Reset password", str(e))
                return HttpResponse(json.dumps(res), status=400)


class Logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request):
        """
        :param request:
        --------------
                    logout request is made
        """
        try:
            request.user
            res = obj1.jsonResponse(True, 'user logged out', '')
            return HttpResponse(json.dumps(res), status=200)
        except Exception:
            res = obj1.jsonResponse(False, 'Something went wrong', '')
            logger.info("Something went wrong!....")
            return HttpResponse(json.dumps(res), status=400)


class SendEmail(GenericAPIView):
    serializer_class = ForgotSerializer

    def post(self, request):
        """
            :param request:
            ---------------
                    request is made for reset template password
            :return:
            -----------
                    will return email where password reset template will be attached
        """
        emailid = request.data["email"]
        try:
            user = User.objects.get(email=emailid)
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
                        'user_token': short[2],
                    }
                )
                tepm = strip_tags(mail_message)
                msg = EmailMultiAlternatives(mail_subject, tepm, emailid, [emailid])
                msg.attach_alternative(mail_message, "text/html")
                msg.send()
                res = obj1.jsonResponse(True, 'Check yout Email', '')
                return HttpResponse(json.dumps(res), status=201)
        except User.DoesNotExist:
            res = obj1.jsonResponse(False, 'Please enter valid Email ID', '')
            logger.info("Invalid Email Entered ", )
            return HttpResponse(json.dumps(res), status=400)
        except Exception as e:
            res = obj1.jsonResponse(False, 'something went wrong', '')
            logger.info("Something went wrong")
            return HttpResponse(json.dumps(res), status=400)
