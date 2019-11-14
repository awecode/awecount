from django.contrib import admin

from .models import BankAccount, ChequeDeposit, ChequeIssue


class ChequeDepositAdmin(admin.ModelAdmin):
    list_filter = ('company',)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)

admin.site.register(BankAccount)
admin.site.register(ChequeIssue)

