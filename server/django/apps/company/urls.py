from django.urls import include, re_path
from rest_framework.routers import SimpleRouter

from apps.company.views import (
    CompanyInvitationViewset,
    CompanyMemberPermissionEndpoint,
    CompanyMemberViewSet,
    CompanyPermissionViewSet,
    CompanyViewset,
    UserCompaniesEndpoint,
    UserCompanyInvitationsViewSet,
    UserCompanySwitchEndpoint,
)

router = SimpleRouter()

router.register(
    r"permissions",
    CompanyPermissionViewSet,
    basename="company-permissions",
)
router.register(
    r"members",
    CompanyMemberViewSet,
    basename="company-members",
)
router.register(
    r"invitations",
    CompanyInvitationViewset,
    basename="company-invitations",
)


urlpatterns = [
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
                "patch": "partial_update",
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
        r"^api/company/(?P<company_slug>[-\w]+)/upload-logo/$",
        CompanyViewset.as_view(
            {
                "post": "upload_logo",
            }
        ),
        name="company-upload-logo",
    ),
    re_path(
        r"^api/company/(?P<company_slug>[-\w]+)/permissions/mine/$",
        CompanyMemberPermissionEndpoint.as_view(),
        name="company-mine",
    ),
    re_path(r"^api/company/(?P<company_slug>[-\w]+)/", include(router.urls)),
    # # Company Permissions
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/permissions/$",
    #     CompanyMemberPermissionEndpoint.as_view(),
    #     name="company-permissions",
    # ),
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/members/$",
    #     CompanyMemberViewSet.as_view(
    #         {
    #             "get": "list",
    #         }
    #     ),
    #     name="company-members",
    # ),
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/members/(?P<pk>[0-9a-f-]+)/$",
    #     CompanyMemberViewSet.as_view(
    #         {
    #             "delete": "destroy",
    #         }
    #     ),
    #     name="company-member-detail",
    # ),
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/invitations/$",
    #     CompanyInvitationViewset.as_view(
    #         {
    #             "get": "list",
    #             "post": "create",
    #         }
    #     ),
    #     name="company-invitations",
    # ),
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/invitations/(?P<pk>[0-9a-f-]+)/$",
    #     CompanyInvitationViewset.as_view(
    #         {
    #             "delete": "destroy",
    #         }
    #     ),
    #     name="company-invitation-detail",
    # ),
    # re_path(
    #     r"^api/company/(?P<company_slug>[-\w]+)/join/(?P<pk>[0-9a-f-]+)/$",
    #     CompanyJoinEndpoint.as_view(),
    #     name="company-join",
    # ),
    # User-related URLs
    # TODO: api/me -> api/user/me
    re_path(
        r"^api/user/me/invitations/$",
        UserCompanyInvitationsViewSet.as_view(
            {
                "get": "list",
                "post": "respond",
            }
        ),
        name="user-company-invitations",
    ),
    re_path(
        r"^api/user/me/companies/$",
        UserCompaniesEndpoint.as_view(),
        name="user-companies",
    ),
    re_path(
        r"^api/user/me/switch-company/$",
        UserCompanySwitchEndpoint.as_view(),
        name="switch-company",
    ),
]
