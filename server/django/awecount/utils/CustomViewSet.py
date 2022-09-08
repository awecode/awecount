from django.core.exceptions import ValidationError, SuspiciousOperation
from inspect import isclass
from rest_framework import mixins, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError as RESTValidationError
from rest_framework.response import Response
from datetime import datetime, timedelta

from awecount.utils.helpers import merge_dicts


class CompanyViewSetMixin(object):
    def get_serializer_class(self):
        if self.action == 'list' and hasattr(self, 'list_serializer_class'):
            return self.list_serializer_class
        return super().get_serializer_class()

    def is_filtered(self):
        return any(x in self.request.query_params if self.request.query_params.get(x) else None for x in
                   self.filterset_class.base_filters.keys())

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

    def perform_create(self, serializer):
        if serializer.instance:
            model = serializer.instance.__class__
        else:
            model = serializer.Meta.model
        if hasattr(model, 'company_id'):
            serializer.validated_data['company_id'] = self.request.company_id
        try:
            serializer.save()
        except ValidationError as e:
            raise RESTValidationError({'detail': e.messages})

    def perform_update(self, serializer):
        if hasattr(serializer.instance.__class__, 'company_id'):
            if serializer.instance.company_id != self.request.company_id:
                raise SuspiciousOperation('Modifying object owned by other company!')
        try:
            serializer.save()
        except ValidationError as e:
            raise RESTValidationError({'detail': e.messages})

    def is_month_filter(self):
        if 'start_date' in self.request.query_params.keys() and 'end_date' in self.request.query_params.keys():
            start_date = datetime.strptime(self.request.query_params['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(self.request.query_params['end_date'], '%Y-%m-%d')
            delta = end_date - start_date
            if delta.days < 33:
                return True


class CollectionViewSet(object):
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

                    # second argument can be a model or a queryset
                    arg_2 = collection[1]
                    if isclass(arg_2):
                        model = arg_2
                        qs = model.objects.all()
                    else:
                        qs = arg_2
                        model = qs.model

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


class GenericSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField(source='__str__')
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ('id', 'name')


class CRULViewSet(CompanyViewSetMixin,
                  CollectionViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    pass
