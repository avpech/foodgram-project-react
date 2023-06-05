from rest_framework.permissions import BasePermission


class Forbidden(BasePermission):
    """Запрет доступа (для исключения ненужных эндпоинтов djoser)."""
    def has_permission(self, request, view):
        return False
