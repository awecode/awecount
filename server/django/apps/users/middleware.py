from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User, Company


class CompanyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_AUTHORIZATION'):
            raw_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
            try:
                valid_data = AccessToken(raw_token)
                user_id = valid_data['user_id']
                try:
                    request.user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    pass
            except:
                pass

        company_obj = None
        if request.user.is_authenticated:
            try:
                if request.user.company:
                    request.__class__.company = request.user.company
            except Company.DoesNotExist:
                pass

        response = self.get_response(request)
        return response

    def authenticate(self, request):
        pass
