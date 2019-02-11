from datetime import datetime
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler

from apps.users.serializers import CompanySerializer, UserSerializer


class JWTCustomAuthentication(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = authenticate(email=data.get('email'), password=data.get('password'))
        context = {}
        if user:
            payload = jwt_payload_handler(user)
            context = {
                'token': jwt_encode_handler(payload),
            }
        else:
            raise APIException({'non_field_errors': 'You have enter wrong ID or password.'})

        # Block user without company
        if user and not user.company:
            raise APIException({'non_field_errors': ['User not registered to any company    .']})

        if user and 'token' in context:
            context['company'] = CompanySerializer(user.company).data
            context['user'] = UserSerializer(user).data
        if user is not None:
            login(request, user)
        return Response(context)


obtain_jwt_token_custom = JWTCustomAuthentication.as_view()
