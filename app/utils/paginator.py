

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 15
#     page_size_query_param = 'page_size'
#     max_page_size = 1000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):

        return Response({
            'links': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link()
                        },
            'count': self.page.paginator.count,
            'results': data,
            # 'page_number': self.page.paginator...,
        })
