from django.contrib import admin

from .models import BankAccount, ChequeDeposit, ChequeIssue, BankCashDeposit


class ChequeDepositAdmin(admin.ModelAdmin):
    list_filter = ('company',)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)


class BankCashDepositAdmin(admin.ModelAdmin):
    list_filter = ('company',)


admin.site.register(BankCashDeposit, BankCashDepositAdmin)

admin.site.register(BankAccount)
admin.site.register(ChequeIssue)
