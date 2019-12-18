import json
import logging
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from .serialized import LoginSerializer, ResetSerializer, UserSerializer, ForgotSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from fundoonotes.settings import file_handler
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
        smd = {'success': False, 'message': "Not registered yet", 'data': []}
        try:
            if username == "" or email == "" or password == "":
                smd['message'] = "one of the details missing"
                logger.error("one of the details missing logging in")
                return HttpResponse(json.dumps(smd), status=400)

            elif User.objects.filter(email=email).exists():
                smd['message'] = "email address is already registered "
                logger.error("email address is already registered  while logging in")
                return HttpResponse(json.dumps(smd), status=400)

            elif User.objects.filter(username=username).exists():
                smd['message'] = "username is already registered "
                logger.error("username is already registered  while logging in")
                return HttpResponse(json.dumps(smd), status=400)
            else:
                user = User.objects.create_user(username=username,
                                                email=email,
                                                password=password,
                                                is_active=True)
                user.save()
                if user is not None:
                    payload = {'username': user.username, 'email': user.email}
                    key = obj.encode_token(payload)
                    short = obj.short_url(key)
                    mail_subject = "Activate your account by clicking below link"
                    mail_message = render_to_string('activate.html', {
                        'user': user.username,
                        'domain': get_current_site(request).domain,
                        'u_token': short[2]
                    })
                    send_mail(mail_subject, mail_message, EMAIL_HOST_USER, [email])
                    smd = {
                        'success': True,
                        'message': 'please check the mail and click on the link  for validation',
                        'data': [],
                    }
                    return HttpResponse(json.dumps(smd), status=201)
        except ValueError as e:
            smd["message"] = "username data not sufficient"
            return HttpResponse(json.dumps(smd), status=400)
        except Exception as e:
            smd["message"] = "something went wrong"
            logger.error("error: %s while loging in ", str(e))
            return HttpResponse(json.dumps(smd), status=400)


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
        print(emailid)
        smd = {'success': False, 'message': "not a vaild email ", 'data': []}
        try:
            user = User.objects.get(email=emailid)
            print(user)
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
                smd = {'success': True, 'message': "check your mail for reset", 'data': []}
                return HttpResponse(json.dumps(smd), status=201)
        except Exception as e:
            print(e)
            smd["success"] = False
            smd['message'] = "email doesn't exist"
            return HttpResponse(json.dumps(smd), status=400)


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
        smd = {"success": False, "message": "not a vaild user", "data": []}
        if request.method == 'POST':
            try:
                password = request.data['password']
                if len(password) < 4 or password == ' ':
                    smd["message"] = "Password should more than 4 digits"
                    logger.info("Password condition failed")
                    return HttpResponse(json.dumps(smd), status=200)
                else:
                    username = obj.decode_tok(token1)
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.save()
                    return redirect("login")
            except Exception as e:
                smd["success"] = False
                smd["message"] = "somethong went wrong"
                logger.info("Coudnt Reset password", str(e))
                return HttpResponse(json.dumps(smd), status=400)


class Logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request):
        """
        :param request:
        --------------
                    logout request is made
        """
        smd = {"success": False, "message": "Invalid User", "data": []}
        try:
            request.user
            smd = {"success": True, "message": "You logged out", "data": []}
            return HttpResponse(json.dumps(smd), status=200)
        except Exception:
            logger.info("Something went wrong!....")
            return HttpResponse(json.dumps(smd), status=400)


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
        smd = {"success": False, "message": "Inavalid user or Email id", "data": []}
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
                smd = {'success': True,
                       'message': "check your mail for reset your password",
                       'data': [],
                       }
                return HttpResponse(json.dumps(smd), status=201)
        except User.DoesNotExist:
            smd['message'] = 'Please enter valid Email ID'
            logger.info("Invalid Email Entered", )
            return HttpResponse(json.dumps(smd), status=400)
        except Exception as e:
            logger.info("Something went wrong", str(e))
            return HttpResponse(json.dumps(smd), status=400)
