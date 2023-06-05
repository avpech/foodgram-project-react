from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение на редактирование объекта только его автором."""
    message = 'У вас недостаточно прав для выполнения данного действия.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author)
