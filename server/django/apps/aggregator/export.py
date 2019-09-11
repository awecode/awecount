import io
import zipfile

from import_export import resources

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


class FilteredResource(resources.ModelResource):
    def get_queryset(self):
        qs = self._meta.model.objects.all()
        if hasattr(self, 'filter_kwargs') and self.filter_kwargs:
            qs = qs.filter(**self.filter_kwargs)
        if hasattr(self, 'exclude_kwargs') and self.exclude_kwargs:
            qs = qs.exclude(**self.exclude_kwargs)
        return qs


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
