from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response


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
    def create(self, request, *args, **kwargs):
        request.data['company_id'] = request.company.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def get_queryset(self):
        if not hasattr(self.request, 'company'):
            raise APIException({'non_field_errors': ['User is not assigned with any company.']})
        company = self.request.company
        return self.serializer_class.Meta.model.objects.filter(company=company)

