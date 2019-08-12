from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class ModuleAccessPermission(permissions.BasePermission):
    message = 'Permission not enough.'

    def has_permission(self, request, view):
        model = view.get_queryset().model
        if hasattr(model, 'key') and model.key and type(model.key) == str:
            _model_name = model.key
        else:
            _model_name = model.__name__
        if not request.user.role:
            raise PermissionDenied({'non_field_errors': ['Please set role for user.']})
        modules = request.user.role.modules

        list_permission = '{}View'.format(_model_name)
        create_permission = '{}Create'.format(_model_name)
        modify_permission = '{}Modify'.format(_model_name)

        if request.method == 'GET' and list_permission not in modules:
            raise PermissionDenied({'non_field_errors': [self.message]})

        if request.method == 'POST' and create_permission not in modules:
            raise PermissionDenied({'non_field_errors': ['User does not have permission to create %s' % _model_name]})

        if request.method == 'PUT' and modify_permission not in modules:
            raise PermissionDenied({'non_field_errors': ['User does not have permission to update %s' % _model_name]})

        return True
