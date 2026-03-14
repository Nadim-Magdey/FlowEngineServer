from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist

class IsActiveOrShowReason(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        if not user.is_active:
            try:
                message = user.userinactivemessage.inactive_message
            except ObjectDoesNotExist:
                message = "Your account is inactive. Please contact support."

            raise PermissionDenied(message)

        return True
