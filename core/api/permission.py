from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from core.security.utils import verify_request


class IsValidClientRequest(BasePermission):

    def has_permission(self, request, view):

        if not verify_request(request):
            raise AuthenticationFailed("Invalid request signature")

        return True
