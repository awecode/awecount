from django.urls import re_path

from .views import UpdateUserOnBoardedEndpoint

urlpatterns = [
    re_path(
        r"^api/me/onboarded/$",
        UpdateUserOnBoardedEndpoint.as_view(),
        name="update-user-onboarded",
    ),
]
