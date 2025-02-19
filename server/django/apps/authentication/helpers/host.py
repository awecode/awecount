from urllib.parse import urlsplit

from django.conf import settings


def base_host(request, is_admin=False, is_space=False, is_app=False):
    """Utility function to return host / origin from the request"""

    if settings.APP_BASE_URL:
        return settings.APP_BASE_URL

    # Calculate the base origin from request
    return str(
        request.META.get("HTTP_ORIGIN")
        or f"{urlsplit(request.META.get('HTTP_REFERER')).scheme}://{urlsplit(request.META.get('HTTP_REFERER')).netloc}"
        or f"""{"https" if request.is_secure() else "http"}://{request.get_host()}"""
    )


def user_ip(request):
    return str(request.META.get("REMOTE_ADDR"))
