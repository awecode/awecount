from rest_framework_simplejwt.tokens import AccessToken

from apps.api.models import AccessKey
from apps.company.models import Company
from apps.users.models import User


class CompanyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get("HTTP_AUTHORIZATION"):
            raw_token = request.META.get("HTTP_AUTHORIZATION").split(" ")[-1]
            try:
                valid_data = AccessToken(raw_token)
                user_id = valid_data["user_id"]
                try:
                    request.user = User.objects.prefetch_related("roles").get(
                        pk=user_id
                    )
                except User.DoesNotExist:
                    pass
            except:
                pass

        elif request.META.get("HTTP_SECRET"):
            secret = request.META.get("HTTP_SECRET")
            request.user = AccessKey.get_user(secret)

        if request.user and request.user.is_authenticated:
            request.__class__.role_modules = request.user.role_modules
            try:
                if request.user.company_id:
                    request.__class__.company_id = request.user.company_id
                if request.user.company:
                    request.__class__.company = request.user.company
            except Company.DoesNotExist:
                pass

        response = self.get_response(request)
        return response

    def authenticate(self, request):
        pass
