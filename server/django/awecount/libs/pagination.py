from rest_framework.pagination import PageNumberPagination as BasePageNumberPagination
from rest_framework.response import Response


# noinspection PyClassHasNoInit
class PageNumberPagination(BasePageNumberPagination):
    aggregate = None
    def get_paginated_response(self, data):
        return Response(self.get_response_data(data))

    def get_response_data(self, data):
        count = self.page.paginator.count
        size = self.page_size
        pagination = {
            'count': count,
            'page': self.page.number,
            'pages': (count + (-count % size)) // size,  # round-up division
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'size': size,
        }
        response_data = {
            'pagination': pagination,
            'results': data
        }
        if self.aggregate:
            response_data['aggregate'] = self.aggregate
        return response_data
