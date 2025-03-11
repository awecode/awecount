from allauth.account.utils import send_email_confirmation
from allauth.core.exceptions import (
    SignupClosedException,
)
from allauth.decorators import rate_limit
from allauth.headless.account import response
from allauth.headless.base.response import (
    AuthenticationResponse,
    ForbiddenResponse,
)
from allauth.headless.base.views import APIView as AllauthAPIView
from allauth.headless.internal.decorators import app_view
from allauth.headless.internal.restkit.response import APIResponse, ErrorResponse
from allauth.socialaccount.internal import flows
from allauth.socialaccount.providers.base import ProviderException
from allauth.socialaccount.providers.base.constants import AuthError
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Error,
)
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView as AllauthOAuth2CallbackView,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.decorators import method_decorator
from requests import RequestException

from .adapters import GoogleOAuth2Adapter
from .inputs import EmailCheckInput


@method_decorator(rate_limit(action="login"), name="handle")
class EmailCheckView(AllauthAPIView):
    input_class = EmailCheckInput

    def post(self, request, *args, **kwargs):
        email = self.input.cleaned_data.get("email")

        user = get_user_model().objects.filter(email=email).first()
        existing = user is not None
        status = "MAGIC_CODE"

        if user and user.has_usable_password():
            status = "CREDENTIALS"

        return APIResponse(
            request,
            status=200,
            data={
                "existing": existing,
                "status": status,
                "signup_allowed": settings.SIGNUP_ALLOWED and not existing,
            },
        )


@method_decorator(rate_limit(action="login"), name="handle")
class RequestEmailVerificationView(AllauthAPIView):
    input_class = EmailCheckInput

    def patch(self, request, *args, **kwargs):
        email = self.input.cleaned_data["email"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return ErrorResponse(
                request,
                exception=AuthError.UNKNOWN,
            )

        sent = send_email_confirmation(request, user, email=email)
        return response.RequestEmailVerificationResponse(
            request, verification_sent=sent
        )


class OAuth2CallbackView(AllauthOAuth2CallbackView):
    # TODO: check allauth.account.internal.flows.login_by_code.request_login_code for stashing state
    def dispatch(self, request, *args, **kwargs):
        if not request.method == "POST":
            return ErrorResponse(
                request,
                exception=AuthError.METHOD_NOT_ALLOWED,
            )

        provider = self.adapter.get_provider()
        state, _resp = self._get_state(request, provider)

        if state is None:
            state = {}

        try:
            import json

            data = json.loads(request.body)
            request.GET = data
        except json.JSONDecodeError:
            return ErrorResponse(
                request,
                exception=AuthError.INVALID_JSON,
            )

        if "error" in request.GET or "code" not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get("error", None)
            if auth_error == self.adapter.login_cancelled_error:
                _error = AuthError.CANCELLED
            else:
                _error = AuthError.UNKNOWN
            raise PermissionDenied("405")

        app = provider.app
        client = self.adapter.get_client(self.request, app)

        try:
            access_token = self.adapter.get_access_token_data(
                request, app, client, pkce_code_verifier=state.get("pkce_code_verifier")
            )
            token = self.adapter.parse_token(access_token)
            if app.pk:
                token.app = app
            login = self.adapter.complete_login(
                request, app, token, response=access_token
            )
            login.token = token
            login.state = state

            try:
                flows.login.complete_login(request, login)
            except ValidationError as e:
                return ErrorResponse(self.request, exception=e)
            except SignupClosedException:
                return ForbiddenResponse(self.request)
            return AuthenticationResponse(self.request)
        except (
            PermissionDenied,
            OAuth2Error,
            RequestException,
            ProviderException,
        ) as e:
            return ErrorResponse(
                request,
                exception=e,
            )


oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = app_view(oauth2_callback)
