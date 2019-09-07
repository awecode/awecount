from rest_framework import mixins, viewsets, status, serializers
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.decorators import action

from awecount.utils.helpers import merge_dicts


class CompanyViewSetMixin(object):
    def get_queryset(self, company_id=None):
        if self.queryset:
            qs = self.queryset
        else:
            qs = self.serializer_class.Meta.model.objects.all()
        if not company_id:
            if not hasattr(self.request, 'company_id'):
                raise APIException({'detail': 'User is not assigned to any company.'})
            company_id = self.request.company_id
        return qs.filter(company_id=company_id)


class GenericSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField(source='__str__')
    id = serializers.ReadOnlyField()


class CreateListRetrieveUpdateViewSet(CompanyViewSetMixin,
                                      mixins.CreateModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.RetrieveModelMixin,
                                      viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, 'delete', and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.

    """

    def get_defaults(self, request=None):
        return {}

    def get_create_defaults(self, request=None):
        return self.get_defaults(request=request)

    def get_update_defaults(self, request=None):
        return self.get_defaults(request=request)

    def get_collections(self, request=None):
        if hasattr(self, 'collections') and self.collections:
            collections_data = {}
            for collection in self.collections:
                if len(collection) > 1:
                    key = collection[0]
                    model = collection[1]
                    qs = model.objects.all()
                    if hasattr(model, 'company_id'):
                        qs = qs.filter(company_id=request.company_id)
                    if len(collection) > 2:
                        serializer = collection[2]
                        data = serializer(qs, many=True).data
                        collections_data[key] = data
                    else:
                        serializer = GenericSerializer
                        data = serializer(qs, many=True).data
                        collections_data[key] = data
            return collections_data

    @action(detail=False, url_path='create-defaults')
    def create_defaults(self, request):
        dct = dict(merge_dicts(self.get_defaults(request), self.get_create_defaults(request)))
        collections = self.get_collections(request)
        if collections:
            dct['collections'] = collections
        return Response(dct)

    @action(detail=True, url_path='update-defaults')
    def update_defaults(self, request, pk):
        dct = dict(merge_dicts(self.get_defaults(request), self.get_update_defaults(request)))
        collections = self.get_collections(request)
        if collections:
            dct['collections'] = collections
        return Response(dct)

    def perform_create(self, serializer):
        serializer.validated_data['company_id'] = self.request.company_id
        serializer.save()
