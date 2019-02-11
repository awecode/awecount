from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from rest_framework_jwt.views import obtain_jwt_token
from awecount.utils.JWTCustomAuthentication import obtain_jwt_token_custom

urlpatterns = [
    path('aweadmin/', admin.site.urls),
    path('auth/', include('rest_framework.urls')),

    path('v1/auth/', obtain_jwt_token_custom),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
