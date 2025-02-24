from django.urls import re_path

from .views import UpdateUserOnBoardedEndpoint, UserViewset

urlpatterns = [
    re_path(
        r"^api/user/me/onboarded/$",
        UpdateUserOnBoardedEndpoint.as_view(),
        name="update-user-onboarded",
    ),
    re_path(
        r"^api/user/me/$",
        UserViewset.as_view(
            {
                "get": "retrieve",
                "patch": "update",
            }
        ),
        name="user",
    ),
    re_path(
        r"^api/user/me/deactivate/$",
        UserViewset.as_view({"patch": "deactivate"}),
        name="deactivate-user",
    ),
]
