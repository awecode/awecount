import sentry_sdk


class SentryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "user") and request.user.is_authenticated:
            user_info = {
                "id": request.user.id,
                "email": request.user.email,
                # "ip_address": request.META.get("REMOTE_ADDR"), # TODO: add ip_address
            }

            sentry_sdk.set_user(user_info)

        if hasattr(request, "company"):
            company_info = {
                "id": request.company.id,
                "name": request.company.name,
            }

            sentry_sdk.set_context("company", company_info)

        response = self.get_response(request)
        return response
