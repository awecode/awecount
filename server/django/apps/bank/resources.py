from apps.bank.models import ChequeIssue
from import_export.resources import ModelResource
from import_export.fields import Field


class ChequeIssueResource(ModelResource):
    bank_account = Field(attribute='bank_account__account_name', column_name='Bank Account')
    # party = Field(attribute='party__name', column_name='Party')
    issued_to = Field(attribute='issued', column_name='Issued To')
    company = Field(attribute='company__name', column_name='Company')

    class Meta:
        model = ChequeIssue
        fields = ['date', 'cheque_no', 'issued_to', 'amount', 'company', 'status']
        export_order = fields
        