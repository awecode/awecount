from import_export.fields import Field

from apps.ledger.models.base import Transaction
from awecounting.libs.resources import PrettyNameModelResource


class TransactionResource(PrettyNameModelResource):
    account = Field(attribute="account__name", column_name="Account")
    date = Field(attribute="journal_entry__date", column_name="Date")

    class Meta:
        model = Transaction
        fields = ["account", "dr_amount", "cr_amount", "date"]
        export_order = ["date", *fields]


class TransactionGroupResource(PrettyNameModelResource):
    fields_mapping = {
        "label": "Label",
        "year": "Year",
        "total_debit": "Total Debit",
        "total_credit": "Total Credit",
    }

    def dehydrate_label(self, bundle):
        return self.get_label(bundle)

    def dehydrate_year(self, bundle):
        return self.get_year(bundle)

    def dehydrate_total_debit(self, bundle):
        return self.get_total_debit(bundle)

    def dehydrate_total_credit(self, bundle):
        return self.get_total_credit(bundle)

    def get_label(self, obj):
        return obj.get("label")

    def get_year(self, obj):
        return obj["year"]

    def get_total_debit(self, obj):
        return obj["total_debit"]

    def get_total_credit(self, obj):
        return obj["total_credit"]

    label = Field(attribute="label", column_name="Label")
    year = Field(attribute="year", column_name="Year")
    total_debit = Field(attribute="total_debit", column_name="Total Debit")
    total_credit = Field(attribute="total_credit", column_name="Total Credit")

    class Meta:
        model = Transaction
        fields = ["label", "year", "total_debit", "total_credit"]
        export_order = fields
