from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param) or 1
        self.current = page_number
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        return page_number
    
    def get_paginated_response(self, data):
        return Response({
            "pages": self.page.paginator.count,
            "current": self.current,
            "results": data,
        })