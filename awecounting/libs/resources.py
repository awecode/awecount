from import_export import resources


class PrettyNameModelResource(resources.ModelResource):
    @classmethod
    def get_pretty_name(cls, name):
        return name.replace("__", " ").replace("_", " ").title()

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        field = super().field_from_django_field(field_name, django_field, readonly)
        field.column_name = cls.get_pretty_name(field_name)
        return field
