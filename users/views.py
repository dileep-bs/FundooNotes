import json
import pdb
import jwt
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django_short_url.models import ShortURL
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from rest_framework.generics import GenericAPIView

from .serialized import LoginSerializer, ResetSerializer, UserSerializer, ForgotSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from fundoonotes.celery import debug_task
# from fundoonotes.fundoonotes.
def index(request):
    return render(request, 'index.html')


class login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        """Posting User login credentials"""
        try:
            username = request.data['username']
            password = request.data['password']
            smd = {'success': False, 'message': "login Failed", 'data': []}
            payload = {'username': username, }
            user = auth.authenticate(username=username, password=password)
            # debug_task.delay()
            try:
                user = auth.authenticate(username=username, password=password)
            except ValueError as e:
                print(e)
            if user is not None:
                jwt_token = {"token": jwt.encode(payload, "secret", algorithm="HS256").decode('utf-8')}
                token = jwt_token['token']
                smd = {'success': True, 'message': "login successful", 'data': [token], }
                return HttpResponse(json.dumps(smd), status=201)
            else:
                smd['message'] = 'Check your password and username'
                return HttpResponse(json.dumps(smd), status=400)
        except Exception as e:
            smd = {'success': False, 'message': "something went wrong", 'data': []}
            return HttpResponse(json.dumps(smd))


class register(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        """Posting User Registration credentials"""
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
                payload = {'username': user.username, 'email': user.email}
                key = jwt.encode(payload, "secret", algorithm="HS256").decode('utf-8')
                currentsite = get_current_site(request)
                url = str(key)
                surl = get_surl(url)
                short = surl.split("/")
                mail_subject = 'Link to activate the account'
                mail_message = render_to_string('activate.html',
                                                {'user': user.username, 'domain': get_current_site(request).domain,
                                                 'token': short[2], })
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
        """Send Mail To reset password"""
        emailid = request.data["email"]
        print(emailid)
        smd = {'success': False,        'message': "not a vaild email ",     'data': []}
        try:
            user = User.objects.get(email=emailid)
            if user is not None:
                payload = {'username': user.username,
                           'email': user.email}

                # key = { jwt.encode(payload, "secret", algorithm="HS256").decode('utf-8')}
                key = jwt.encode(payload, "secret", algorithm="HS256").decode('utf-8')
                currentsite = get_current_site(request)
                url = str(key)
                surl = get_surl(url)
                short = surl.split("/")
                mail_subject = "Reset your password by clicking below link"
                mail_message = render_to_string('verify.html',                           {'user': user.username,
                                                 'domain': get_current_site(request).domain,
                                                 'token': short[2]})
                store=mail_message
                send_mail(mail_subject, mail_message, EMAIL_HOST_USER, [emailid])
                smd = {'success': True,        'message': "check your mail for reset",             'data': [key]}
                return HttpResponse(json.dumps(smd), status=201)
        except Exception as e:
            print(e)
            smd["success"] = False
            smd['message'] = "email doesn't exist"
            return HttpResponse(json.dumps(smd), status=400)


def activate(request, token):
    try:
        tokenobj = ShortURL.objects.get(surl=token)
        token = tokenobj.lurl
        print(token)
        user_details = jwt.decode(token, 'secret', algorithms='HS256')
        user_name = user_details['username']
        try:
            user = User.objects.get(username=user_name)
        except ObjectDoesNotExist as e:
            print(e)
        if user is not None:
            user.is_active = True
            user.save()
            messages.info(request, "your account is active now")
            return redirect('/login')
        else:
            return redirect('register')
    except KeyError:
        messages.info(request, 'mail sending failed')
        return redirect('/register')


def verify(request, token):
    try:
        tokenobj = ShortURL.objects.get(surl=token)
        token = tokenobj.lurl
        print(token)
        user_details = jwt.decode(token, 'secret', algorithms='HS256')
        username = user_details['username']
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist as e:
            print(e)
        if user is not None:
            # currentsite = get_current_site(request)
            # string = str(currentsite) + '/resetpassword/' + username + '/'
            username1 = {'userReset': user.username}
            print(username1)
            messages.info(request, "reset")
            return redirect('/api/reset_password/' + str(token) + '/')
        else:
            messages.info("Invalid user")
            return redirect('register')
    except Exception as e:
        print(str(e))
        return redirect('resetmail')


class reset_password(GenericAPIView):
    serializer_class = ResetSerializer

    def post(self, request, token):
        """ResetPassword for Authenticated user"""
        if request.method == 'POST':
            password = request.data['password']
            user_details = jwt.decode(token, 'secret', algorithms='HS256')
            username = user_details['username']
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                messages.info(request, "password reset successfully")
                return redirect("login")
        return render(request, 'resetpassword.html')


def page(request):
    return render(request, 'page.html')


class logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request):
        """User logout"""
        smd = {"success": False, "message": "not a vaild user", "data": []}
        try:
            user = request.user
            smd = {"success": True, "message": "logged out", "data": []}
            return HttpResponse(json.dumps(smd), status=200)
        except Exception:
            return HttpResponse(json.dumps(smd), status=400)


class SendEmail(GenericAPIView):
    serializer_class = ForgotSerializer
    def post(self,request):
        """User email"""
        smd = {"success": False, "message": "Email sending fail", "data": []}
        emailid = request.data["email"]
        user1=request.user
        try:
            user = User.objects.get(email=emailid)
            if user is not None:
                subject, from_email, to = 'Email Validation', EMAIL_HOST_USER, emailid
                html_content = render_to_string('Validation.html', {'user': user.username,  'domain': get_current_site(request).domain})  # render with dynamic value
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                smd = {"success": True, "message": "Success", "data": [html_content]}
                return HttpResponse(json.dumps(smd), status=200)
        except Exception:
            smd = {"success": False, "message": "Inavalid user or Email id", "data": []}
            return HttpResponse(json.dumps(smd), status=400)



