from django.contrib.auth import authenticate, login
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework_jwt.views import ObtainJSONWebToken


class JWTCustomAuthentication(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = authenticate(username=data.get('username'), password=data.get('password'))
        context = {}

        if user:
            payload = jwt_payload_handler(user)
            context = {
                'token': jwt_encode_handler(payload),
            }
        else:
            raise APIException({'non_field_errors': 'You have enter wrong ID or password.'})

        # Block user without role
        if user and (not user.role or not user.role.modules):
            raise APIException({'non_field_errors': ['User have no roles.']})
        # Block web user to access mobile login
        if user and 'HTTP_PLATFORM' in request.META and request.META.get(
                'HTTP_PLATFORM') == 'Android' and not user.is_mobile_user:
            raise APIException({'non_field_errors': ['You are not mobile user. Please check back office.']})
        # Block mobile user to access web login
        if user and 'HTTP_PLATFORM' not in request.META and user.is_mobile_user:
            raise APIException({'non_field_errors': ['You are not web user. Please check back office.']})
        # Update token json with user data
        if user and 'token' in context:
            context.update(user.data)
        if user is not None:
            login(request, user)
        return Response(context)


obtain_jwt_token_custom = JWTCustomAuthentication.as_view()
