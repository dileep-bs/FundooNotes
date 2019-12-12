from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
# from rest_framework_simplejwt import views as jwt_views
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Fundoonotes API')



urlpatterns = [

    path('admin/', admin.site.urls),
    path('', schema_view),
    url('api/',include('users.urls')),
    url('api/',include('notes.urls')),
    path('sociallogin/',include('sociallogin.urls')),
    # path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]