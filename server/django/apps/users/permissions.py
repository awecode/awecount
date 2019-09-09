from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .permission_modules import MODULES


class ModuleAccessPermission(permissions.BasePermission):
    message = 'Permission not enough.'

    def has_permission(self, request, view):
        model = view.get_queryset().model
        if hasattr(model, 'key') and model.key and type(model.key) == str:
            _model_name = model.key
        else:
            _model_name = model.__name__
        modules = request.user.role_modules

        list_permission = '{}View'.format(_model_name)
        create_permission = '{}Create'.format(_model_name)
        modify_permission = '{}Modify'.format(_model_name)
        cancel_permission = '{}Cancel'.format(_model_name)

        if view.action == 'cancel' and request.method == 'POST' and cancel_permission in MODULES:
            if cancel_permission not in modules:
                raise PermissionDenied({'detail': 'User does not have permission to cancel %s.' % _model_name})
        else:
            if request.method == 'GET' and list_permission not in modules:
                raise PermissionDenied({'detail': self.message})

            if request.method == 'POST' and create_permission not in modules:
                raise PermissionDenied({'detail': 'User does not have permission to create %s.' % _model_name})

            if request.method == 'PUT' and modify_permission not in modules:
                raise PermissionDenied({'detail': 'User does not have permission to update %s.' % _model_name})

        return True
