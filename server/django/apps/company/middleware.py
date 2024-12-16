from django.core.exceptions import ImproperlyConfigured

from .models import Company


class CompanyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "The Company middleware requires authentication middleware to be installed."
                "Edit your MIDDLEWARE setting to insert "
                "'django.contrib.sessions.middleware.AuthenticationMiddleware' before "
                "'apps.company.middleware.CompanyMiddleware'."
            )

        request.company = None

        if not request.user.is_authenticated:
            return self.get_response(request)

        if getattr(request.user, "is_api", False):
            company_slug = request.kwargs.get("company_slug", None)
            if company_slug:
                try:
                    company = Company.objects.get(
                        slug=company_slug,
                        company_members__member=request.user,
                    )
                    request.company = company
                except Company.DoesNotExist:
                    pass
        else:
            request.company = request.user.company

        return self.get_response(request)
