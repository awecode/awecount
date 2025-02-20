from django.urls import re_path

from apps.company.views import (
    CompanyInvitationsViewset,
    CompanyJoinEndpoint,
    CompanyPermissionEndpoint,
    CompanyViewset,
    UserCompaniesEndpoint,
    UserCompanyInvitationsViewSet,
    UserCompanySwitchEndpoint,
)

urlpatterns = [
    # Company-related URLs
    re_path(
        r"^api/company/$",
        CompanyViewset.as_view(
            {
                "post": "create",
            }
        ),
        name="company-create",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/$",
        CompanyViewset.as_view(
            {
                "get": "retrieve",
                "put": "update",
            }
        ),
        name="company-info",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/delete/$",
        CompanyViewset.as_view(
            {
                "delete": "destroy",
            }
        ),
        name="company-delete",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/permissions/$",
        CompanyPermissionEndpoint.as_view(),
        name="company-permissions",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/invitations/$",
        CompanyInvitationsViewset.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="company-invitations",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/invitations/(?P<pk>[0-9a-f-]+)/$",
        CompanyInvitationsViewset.as_view(
            {
                "delete": "destroy",
            }
        ),
        name="company-invitation-detail",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/join/(?P<pk>[0-9a-f-]+)/$",
        CompanyJoinEndpoint.as_view(),
        name="company-join",
    ),
    # User-related URLs
    # TODO: api/me -> api/user/me
    re_path(
        r"^api/me/invitations/$",
        UserCompanyInvitationsViewSet.as_view(
            {
                "get": "list",
                "post": "respond",
            }
        ),
        name="user-company-invitations",
    ),
    re_path(
        r"^api/me/companies/$",
        UserCompaniesEndpoint.as_view(),
        name="user-companies",
    ),
    re_path(
        r"^api/me/switch-company/$",
        UserCompanySwitchEndpoint.as_view(),
        name="switch-company",
    ),
]
