"""
Custom Pagination
"""
from rest_framework.pagination import PageNumberPagination

class AppPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # The query parameter to specify the page size
    max_page_size = 100  # Maximum limit for page size
