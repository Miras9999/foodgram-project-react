from rest_framework import permissions


class RecipeAuthorOrReadOnly:

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and 'favorite' in request.resolver_match.route)
            or (request.user.is_authenticated
                and 'shopping_cart' in request.resolver_match.route)
        )


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
        )


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.method == 'POST'
                or (request.method == 'DELETE'
                    and request.user.is_authenticated))

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj
                or request.user.is_staff)
