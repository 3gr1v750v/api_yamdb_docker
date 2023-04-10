from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Анонимные пользователи могут запрашивать данные.
    Пользователь с ролью 'администратор' или администратор могут изменять
    данные.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsOwnerModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Анонимные пользователи могут запрашивать данные.
    Пользователь с ролью 'администратор', администраторы проекта и
    пользователи с ролью 'модератор' могут изменять данные.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (obj.author == request.user)
            or (request.user.is_admin or request.user.is_moderator)
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Доступ к данным есть только у администратора, или пользователя с ролью
    'администратор'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsProfileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
