from datetime import datetime
from inspect import isclass

from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db.models import Q
from django.http import Http404
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as RESTValidationError
from rest_framework.response import Response

from awecount.libs.helpers import merge_dicts


class CompanyViewSetMixin(object):
    def get_serializer_class(self):
        if self.action == "list" and hasattr(self, "list_serializer_class"):
            return self.list_serializer_class
        return super().get_serializer_class()

    def is_filtered(self):
        return any(
            x in self.request.query_params if self.request.query_params.get(x) else None
            for x in self.filterset_class.base_filters.keys()
        )

    def is_filtered_by_date(self):
        return (
            "start_date" in self.request.query_params
            and "end_date" in self.request.query_params
        )

    def get_queryset(self, company_id=None):
        if self.queryset:
            qs = self.queryset
        else:
            qs = self.serializer_class.Meta.model.objects.all()
        if not company_id:
            if not hasattr(self.request, "company_id"):
                raise APIException({"detail": "User is not assigned to any company."})
            company_id = self.request.company_id
        return qs.filter(company_id=company_id)

    def perform_create(self, serializer):
        if serializer.instance:
            model = serializer.instance.__class__
        else:
            model = serializer.Meta.model
        if hasattr(model, "company_id"):
            serializer.validated_data["company_id"] = self.request.company_id
        try:
            serializer.save()
        except ValidationError as e:
            raise RESTValidationError({"detail": e.messages})

    def perform_update(self, serializer):
        if hasattr(serializer.instance.__class__, "company_id"):
            if serializer.instance.company_id != self.request.company_id:
                raise SuspiciousOperation("Modifying object owned by other company!")
        try:
            serializer.save()
        except ValidationError as e:
            raise RESTValidationError({"detail": e.messages})

    def is_month_filter(self):
        if (
            "start_date" in self.request.query_params.keys()
            and "end_date" in self.request.query_params.keys()
        ):
            start_date = datetime.strptime(
                self.request.query_params["start_date"], "%Y-%m-%d"
            )
            end_date = datetime.strptime(
                self.request.query_params["end_date"], "%Y-%m-%d"
            )
            delta = end_date - start_date
            if delta.days < 33:
                return True


class CollectionViewSet(object):
    def get_defaults(self, request=None, *args, **kwargs):
        return {}

    def get_create_defaults(self, request=None, *args, **kwargs):
        return self.get_defaults(request=request)

    def get_update_defaults(self, request=None, *args, **kwargs):
        return self.get_defaults(request=request)

    def get_collection_results(self, request=None, collection=[]):
        # second argument can be a model or a queryset
        arg_2 = collection[1]
        if isclass(arg_2):
            model = arg_2
            qs = model.objects.all()
        else:
            qs = arg_2
            model = qs.model
        if hasattr(model, "company_id"):
            qs = qs.filter(company_id=request.company_id)

        paginate = True
        if len(collection) > 3:
            paginate = collection[3]

        search_fields = []
        if len(collection) > 4:
            search_fields = collection[4]

        search_keyword = request.query_params.get("search")
        if search_keyword and search_fields:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_keyword})

            # Apply the filter to the queryset
            qs = qs.filter(query)
            # qs = qs.filter(name__icontains=search_keyword)

        serializer_class = GenericSerializer
        if len(collection) > 2:
            serializer_class = collection[2]

        if paginate:
            page = self.paginate_queryset(qs)
            serializer = serializer_class(page, many=True)
            self.paginator.page_size = 30
            paginated_response = self.get_paginated_response(serializer.data)
            data = paginated_response.data
            return data
        else:
            serializer = serializer_class(qs, many=True)
            return serializer.data

    def get_collections(self, request=None, *args, **kwargs):
        if hasattr(self, "collections") and self.collections:
            collections_data = {}
            for collection in self.collections:
                if len(collection) > 1:
                    key = collection[0]
                    collections_data[key] = self.get_collection_results(
                        request=request, collection=collection
                    )
            return collections_data

    @action(detail=False, url_path="create-defaults")
    def create_defaults(self, request, *args, **kwargs):
        dct = dict(
            merge_dicts(self.get_defaults(request), self.get_create_defaults(request))
        )
        collections = self.get_collections(request)
        if collections:
            dct["collections"] = collections
        return Response(dct)

    @action(detail=False, url_path="create-defaults/(?P<slug>[^/.]+)")
    def create_defaults_by_slug(self, request, slug, *args, **kwargs):
        collection = next(
            (entry for entry in self.collections if entry[0] == slug), None
        )
        if not collection:
            raise Http404
        response = {}
        if len(collection) > 1:
            response = self.get_collection_results(
                request=request, collection=collection
            )
        return Response(response)

    @action(detail=True, url_path="update-defaults")
    def update_defaults(self, request, pk, *args, **kwargs):
        dct = dict(
            merge_dicts(self.get_defaults(request), self.get_update_defaults(request))
        )
        collections = self.get_collections(request)
        if collections:
            dct["collections"] = collections
        return Response(dct)


class GenericSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField(source="__str__")
    id = serializers.ReadOnlyField()

    class Meta:
        fields = ("id", "name")


class CRULViewSet(
    CompanyViewSetMixin,
    CollectionViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass
