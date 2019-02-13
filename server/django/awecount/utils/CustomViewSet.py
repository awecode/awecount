from rest_framework import mixins, viewsets
from rest_framework.exceptions import APIException


class CreateListRetrieveUpdateViewSet(mixins.CreateModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.RetrieveModelMixin,
                                      viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, 'delete', and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.

    """

    def get_queryset(self):
        if not hasattr(self.request, 'company'):
            raise APIException({'error': 'User is not assigned with any company.'})
        company = self.request.company
        return self.serializer_class.Meta.model.objects.filter(company=company)

