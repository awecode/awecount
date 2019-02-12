from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

from apps.users.models import User, Company


class CompanyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_AUTHORIZATION'):
            token_key = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
            token = {'token': token_key}

            try:
                valid_data = VerifyJSONWebTokenSerializer().validate(token)
                user = valid_data['user']
                request.user = user
                try:
                    request.user = User.objects.get(pk=user.id)
                except User.DoesNotExist:
                    pass
            except:
                pass

        company_obj = None
        if request.user.is_authenticated:
            try:
                company_obj = Company.objects.get(id=request.user.company.id)
            except Company.DoesNotExist:
                pass

            request.__class__.company = company_obj.id
        #
        response = self.get_response(request)
        return response

    def authenticate(self, request):
        pass
