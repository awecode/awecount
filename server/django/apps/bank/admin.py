from django.contrib import admin

from .models import BankAccount, ChequeDepositRow, ChequeDeposit, Bank, BankBranch, ChequeVoucher

admin.site.register(BankAccount)


class ChequeDepositRowTabular(admin.TabularInline):
    model = ChequeDepositRow


class ChequeDepositAdmin(admin.ModelAdmin):
    inlines = (ChequeDepositRowTabular,)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)
admin.site.register(Bank)
admin.site.register(BankBranch)
admin.site.register(ChequeVoucher)

