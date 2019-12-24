from django.urls import path
# from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.views import ObtainJSONWebToken as v

from . import views


urlpatterns =[
                path("login/",views.Login.as_view(),name='login'),
                path("register/",views.Register.as_view(),name='register'),
                path('activate/<token2>/',views.activate,name='activate'),
                path('verify/<token1>/',views.verify,name='verify'),
                # path("page",views.page,name='page'),
                path("logout/",views.Logout.as_view(),name='logout'),
                path('sendmail/',views.Sendmail.as_view(),name='rpassmail'),
                path('resetpassword/<token1>/',views.resetpassword.as_view(),name='resetpassword'),
                path("template/", views.SendEmail.as_view(),name='sendmail'),
                # path('api/token/', v.as_view(), name='token_obtain_pair'),
                # path('api/token/refresh/', v.as_view(), name='token_refresh'),
]
