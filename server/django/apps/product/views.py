import requests
from django.http import HttpResponse


def book_by_isbn(request, isbn):
    url = "https://thuprai.com/book/isbn/{}".format(isbn)
    requests_response = requests.get(url)
    django_response = HttpResponse(
        content=requests_response.content,
        status=requests_response.status_code,
        charset="utf-8",
        content_type=requests_response.headers["Content-Type"],
    )
    return django_response
