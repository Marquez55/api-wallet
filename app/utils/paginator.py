from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data, key_name):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            key_name: data
        })

    def get_next_link(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return self.request.build_absolute_uri(
            self.request.path) + f'?page={page_number}&page_size={self.page.paginator.per_page}'

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        return self.request.build_absolute_uri(
            self.request.path) + f'?page={page_number}&page_size={self.page.paginator.per_page}'