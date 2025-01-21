from django.shortcuts import get_object_or_404
from django.urls import resolve
from django.utils.functional import SimpleLazyObject

from .models import Company


def get_company(request):
    if hasattr(request, "_cached_company"):
        return request._cached_company

    if not request.user.is_authenticated:
        return None

    company = None

    resolver_match = resolve(request.path_info)
    company_slug = resolver_match.kwargs.get("company_slug")

    if not company_slug:
        return None

    company = get_object_or_404(
        Company,
        slug=company_slug,
        company_members__member=request.user,
    )

    request._cached_company = company
    return request._cached_company


class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        request.company = SimpleLazyObject(lambda: get_company(request))
        response = self.get_response(request)
        return response
