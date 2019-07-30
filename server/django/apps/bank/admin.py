from django.contrib import admin

from .models import BankAccount, ChequeDepositRow, ChequeDeposit

admin.site.register(BankAccount)


class ChequeDepositRowTabular(admin.TabularInline):
    model = ChequeDepositRow


class ChequeDepositAdmin(admin.ModelAdmin):
    inlines = (ChequeDepositRowTabular,)


admin.site.register(ChequeDeposit, ChequeDepositAdmin)
