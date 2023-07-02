from apps.bank.models import ChequeIssue
from import_export.resources import ModelResource
from import_export.fields import Field


class ChequeIssueResource(ModelResource):
    bank_account = Field(attribute='bank_account__account_name', column_name='Bank Account')
    party = Field(attribute='party__name', column_name='Party')
    company = Field(attribute='company__name', column_name='Company')
    
    class Meta:
        model = ChequeIssue