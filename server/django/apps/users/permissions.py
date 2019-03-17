from rest_framework import permissions
from rest_framework.exceptions import APIException


class ModuleAccessPermission(permissions.BasePermission):
    message = 'Permission not enough.'

    def has_permission(self, request, view):
        _model_name = view.get_queryset().model.__name__
        modules = request.user.role.modules

        list_permission = f'{_model_name}View'
        create_permission = f'{_model_name}Create'
        modify_permission = f'{_model_name}Modify'

        if request.method == 'GET' and list_permission not in modules:
            raise APIException({'non_field_errors': [self.message]})

        if request.method == 'POST' and create_permission not in modules:
            raise APIException({'non_field_errors': ['User do not have permission to create %s' % _model_name]})

        if request.method == 'PUT' and modify_permission not in modules:
            raise APIException({'non_field_errors': ['User do not have permission to update %s' % _model_name]})

        return True
