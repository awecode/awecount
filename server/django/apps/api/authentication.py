from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header

from apps.api.models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API Key authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Api-Key ".  For example:

        Authorization: Api-Key eVWWx1Ko.Xq7CkcYWKWVxLD07krVEubPE6gYO86SJ6yCmuTM28jSmc7g6
    """

    keyword = "Api-Key"
    model = APIKey

    def authenticate(self, request, *args, **kwargs):
        authorization = get_authorization_header(request)

        if not authorization:
            return None

        keyword, found, key = authorization.decode().partition(" ")

        if not found or keyword != self.keyword:
            return None

        if not key:
            raise exceptions.AuthenticationFailed(
                _("Invalid token header. No credentials provided.")
            )

        return self.authenticate_credentials(key)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            api_key, is_valid = model.objects.validate_key(key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not is_valid:
            raise exceptions.AuthenticationFailed(_("API key is not valid."))

        return api_key.user, None

    def authenticate_header(self, request, *args, **kwargs):
        return self.keyword

    def get_model(self):
        return self.model
