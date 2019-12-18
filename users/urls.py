from django.urls import path
from . import views

urlpatterns =[
                path("login/",views.Login.as_view(),name='login'),
                path("register/",views.Register.as_view(),name='register'),
                path('activate/<token>/',views.activate,name='activate'),
                path('verify/<token1>/',views.verify,name='verify'),
                # path("page",views.page,name='page'),
                path("logout/",views.Logout.as_view(),name='logout'),
                path('sendmail/',views.Sendmail.as_view(),name='rpassmail'),
                path('resetpassword/<token1>/',views.resetpassword.as_view(),name='resetpassword'),
                path("template/", views.SendEmail.as_view(),name='sendmail'),
]
