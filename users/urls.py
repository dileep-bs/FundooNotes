from django.urls import path
from . import views

urlpatterns =[
                path('',views.index,name='index'),
                path("login/",views.login.as_view(),name='login'),
                path("register/",views.register.as_view(),name='register'),
                path('activate/<token>/',views.activate,name='activate'),
                path('verify/<token>/',views.verify,name='verify'),
                path("page",views.page,name='page'),
                path("logout/",views.logout.as_view(),name='logout'),
                path('sendmail/',views.sendmail.as_view(),name='resetmail'),
                path('reset_password/<token>/',views.reset_password.as_view(),name='resetmail'),
                path("template/", views.SendEmail.as_view(),name='sendmail'),
                # path('hello/', views.HelloView.as_view(), name='hello'),
]
