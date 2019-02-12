from datetime import datetime
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase
from six import text_type

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


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)
        data['company'] = CompanySerializer(self.user.company).data
        data['user'] = UserSerializer(self.user).data
        return data


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()
