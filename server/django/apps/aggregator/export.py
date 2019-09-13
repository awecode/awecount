import io
import zipfile
import json

import tablib
from django.apps import apps
from django.core.exceptions import SuspiciousOperation
from import_export import resources, widgets

from apps.bank.models import BankAccount, ChequeDeposit, ChequeVoucher, ChequeDepositRow
from apps.ledger.models import Category, Account, Party, PartyRepresentative
from apps.product.models import Unit, Brand, Category as InventoryCategory, InventoryAccount, Item
from apps.tax.models import TaxScheme
from apps.voucher.models import SalesVoucher, SalesDiscount, PurchaseDiscount, InvoiceDesign, JournalVoucher, JournalVoucherRow, \
    DebitNoteRow, CreditNoteRow, PurchaseVoucherRow, SalesVoucherRow, DebitNote, CreditNote, PurchaseVoucher

COMPANY_FILTERS = [
    # Bank
    BankAccount, ChequeDeposit, ChequeVoucher,
    # Ledger
    Category, Account, Party,
    # Product
    Unit, Brand, InventoryCategory, InventoryAccount, Item,
    # Tax
    TaxScheme,
    # Voucher Helpers
    SalesDiscount, PurchaseDiscount, InvoiceDesign,
    # Vouchers
    JournalVoucher, SalesVoucher, PurchaseVoucher, CreditNote, DebitNote
]

# JournalEntry ?
COMPANY_ID_ACCESSOR_FILTERS = [
    # Bank
    ChequeDepositRow,
    # Ledger
    PartyRepresentative,
    # Vouchers
    JournalVoucherRow, SalesVoucherRow, PurchaseVoucherRow, CreditNoteRow, DebitNoteRow
]


class JSONWidget(widgets.Widget):
    """ Convert data into JSON for serialization.
    """

    def clean(self, value, row=None, *args, **kwargs):
        return json.loads(value)

    def render(self, value, obj=None):
        if value is None:
            return ""
        return json.dumps(value)


class JSONResourceMixin(object):
    """ Override ModelResource to provide JSON field support.
    """

    @classmethod
    def widget_from_django_field(cls, f, default=widgets.Widget):

        if f.get_internal_type() in ('JSONField',):
            return JSONWidget
        else:
            return super().widget_from_django_field(f)


class FilteredResource(JSONResourceMixin, resources.ModelResource):
    def get_queryset(self):
        qs = self._meta.model.objects.all()
        if hasattr(self, 'filter_kwargs') and self.filter_kwargs:
            qs = qs.filter(**self.filter_kwargs)
        if hasattr(self, 'exclude_kwargs') and self.exclude_kwargs:
            qs = qs.exclude(**self.exclude_kwargs)
        return qs
    
    def export_book(self):
        import ipdb
        ipdb.set_trace()

    class Meta:
        exclude = ('extra_data')


def get_csvs(company_id):
    csvs = {}
    for model in COMPANY_FILTERS:
        resource = resources.modelresource_factory(model=model, resource_class=FilteredResource)()
        resource.filter_kwargs = {'company_id': company_id}
        data = resource.export()
        if len(data):
            key = '{}__{}'.format(model.__name__, model._meta.app_label)
            csvs[key] = data.csv
    for model in COMPANY_ID_ACCESSOR_FILTERS:
        resource = resources.modelresource_factory(model=model, resource_class=FilteredResource)()
        resource.filter_kwargs = {model.company_id_accessor: company_id}
        data = resource.export()
        if len(data):
            key = '{}__{}'.format(model.__name__, model._meta.app_label)
            csvs[key] = data.csv
    return csvs


def zip_csvs(csvs):
    zipped_file = io.BytesIO()
    with zipfile.ZipFile(zipped_file, 'w') as f:
        for key, csv in csvs.items():
            f.writestr("{}.csv".format(key), csv)
    zipped_file.seek(0)
    return zipped_file


def get_zipped_csvs(company_id):
    csvs = get_csvs(company_id)
    zip = zip_csvs(csvs)
    return zip


def import_zipped_csvs(company_id, zipped_file):
    if not zipped_file:
        raise SuspiciousOperation('Invalid Zip File.')
    # TODO Check company id
    with zipfile.ZipFile(zipped_file, 'r') as zip:
        dct = {}
        for file_name in zip.namelist():
            file_contents = zip.read(file_name).decode('utf-8')
            dataset = tablib.Dataset()
            dataset.load(file_contents, format='csv')
            filename_sans_ext = file_name.strip('.csv')
            splits = filename_sans_ext.split('__')
            if len(splits) < 2:
                raise SuspiciousOperation('Invalid Zip File.')
            model_name = splits[0]
            app_name = splits[1]
            try:
                model = apps.get_model(app_label=app_name, model_name=model_name)
            except LookupError:
                raise SuspiciousOperation('Invalid Zip File.')
            if not (model in COMPANY_FILTERS or model in COMPANY_ID_ACCESSOR_FILTERS):
                raise SuspiciousOperation('Invalid Zip File.')
            resource = resources.modelresource_factory(model=model, resource_class=FilteredResource)()
            result = resource.import_data(dataset, dry_run=True)
            if result.has_errors():
                raise SuspiciousOperation('Importing failed.')
            else:
                ret = resource.import_data(dataset, dry_run=False, use_transactions=True)
                dct[filename_sans_ext] = ret.totals
        return dct

