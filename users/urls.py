from django.urls import path
from . import views

urlpatterns =[
                path("login/",views.login.as_view(),name='login'),
                path("register/",views.register.as_view(),name='register'),
                path('activate/<token>/',views.activate,name='activate'),
                path('verify/<token1>/',views.verify,name='verify'),
                path("logout/",views.logout.as_view(),name='logout'),
                path('sendmail/',views.sendmail.as_view(),name='sendmail'),
                path('resetpassword/<tok>/',views.resetpassword.as_view(),name='resetpassword'),
                path("template/", views.SendEmail.as_view(),name='sendmail'),
]
