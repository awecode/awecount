from import_export import resources
from .models import SalesVoucher, SalesVoucherRow


class PrettyNameMixin:
    @classmethod
    def get_pretty_name(cls, name):
        return name.replace('__', ' ').replace('_', ' ').title()

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        FieldWidget = cls.widget_from_django_field(django_field)
        widget_kwargs = cls.widget_kwargs_for_field(field_name)
        field = cls.DEFAULT_RESOURCE_FIELD(
            attribute=field_name,
            column_name=cls.get_pretty_name(field_name),
            widget=FieldWidget(**widget_kwargs),
            readonly=readonly,
            default=django_field.default,
        )
        return field

INVOICE_EXCLUDES = ('party', 'discount_obj', 'bank_account', 'company', 'fiscal_year')

class InvoiceResource(PrettyNameMixin, resources.ModelResource):
    id = resources.Field('id', column_name='ID')
    voucher_no = resources.Field('voucher_no', column_name='Bill No.')
    party_name = resources.Field('party__name', column_name='Party')
    
    

    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class SalesVoucherResource(PrettyNameMixin, resources.ModelResource):
    class Meta:
        model = SalesVoucher
        exclude = INVOICE_EXCLUDES


class SalesVoucherRowResource(PrettyNameMixin, resources.ModelResource):
    class Meta:
        model = SalesVoucherRow
