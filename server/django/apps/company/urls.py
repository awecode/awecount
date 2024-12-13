from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.company.views import (
    CompanyInvitationsViewset,
    CompanyJoinEndpoint,
    CompanyPermissionEndpoint,
    UserCompanyInvitationsViewSet,
)

router = DefaultRouter()

urlpatterns = [
    path(
        "api/company/<slug:company_slug>/invitations/",
        CompanyInvitationsViewset.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="company-invitations",
    ),
    path(
        "api/company/<slug:company_slug>/invitations/<uuid:pk>/",
        CompanyInvitationsViewset.as_view(
            {
                "delete": "destroy",
            }
        ),
        name="company-invitation-detail",
    ),
    path(
        "api/company/<slug:company_slug>/join/<uuid:pk>/",
        CompanyJoinEndpoint.as_view(),
        name="company-join",
    ),
    path(
        "api/invitations/",
        UserCompanyInvitationsViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="user-company-invitations",
    ),
    path(
        "api/company/<slug:company_slug>/permissions/",
        CompanyPermissionEndpoint.as_view(),
        name="company-permissions",
    ),
]
