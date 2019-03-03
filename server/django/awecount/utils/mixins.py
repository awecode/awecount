from rest_framework.decorators import action
from awecount.utils import delete_rows


class InputChoiceMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        if self.action in ('choices',):
            self._paginator = None
        return self._paginator

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        choice_fields = None
        if hasattr(self, 'choice_fields'):
            choice_fields = self.choice_fields
        if self.action in ('choices',):
            return serializer_class(*args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    @action(detail=False)
    def choices(self, request):
        return self.list(request)


class DeleteRows(object):
    def update(self, request, *args, **kwargs):
        params = request.data
        delete_rows(params.get('deleted_rows', None), self.row)
        return super(DeleteRows, self).update(request, *args, **kwargs)
