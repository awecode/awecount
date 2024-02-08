from django.contrib import admin

from .models import (
    BankAccount,
    BankCashDeposit,
    ChequeDeposit,
    ChequeIssue,
    FundTransfer,
    FundTransferTemplate,
)


class ChequeDepositAdmin(admin.ModelAdmin):
    list_filter = ("company",)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)


class BankCashDepositAdmin(admin.ModelAdmin):
    list_filter = ("company",)


admin.site.register(BankCashDeposit, BankCashDepositAdmin)


class BankAccountAdmin(admin.ModelAdmin):
    list_filter = ("company",)
    search_fields = ("name", "account_number", "bank_name", "branch_name")


admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(ChequeIssue)


class FundTransferAdmin(admin.ModelAdmin):
    list_filter = ("company", "status")


admin.site.register(FundTransfer, FundTransferAdmin)


class FundTransferTemplateAdmin(admin.ModelAdmin):
    list_filter = ("company",)
    autocomplete_fields = ("from_account", "to_account", "transaction_fee_account")


admin.site.register(FundTransferTemplate, FundTransferTemplateAdmin)
