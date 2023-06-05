from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPagination(PageNumberPagination):
    """Паджинация с поддержкой указания количества получаемых объектов."""
    page_size_query_param = 'limit'
