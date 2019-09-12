from django.contrib import admin

from .models import BankAccount, ChequeDepositRow, ChequeDeposit, ChequeVoucher

class ChequeDepositRowTabular(admin.TabularInline):
    model = ChequeDepositRow


class ChequeDepositAdmin(admin.ModelAdmin):
    inlines = (ChequeDepositRowTabular,)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)

admin.site.register(BankAccount)
admin.site.register(ChequeVoucher)

