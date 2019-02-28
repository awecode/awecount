from rest_framework.decorators import action


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
