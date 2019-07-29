from django.db import models

# Create your models here.
from apps.ledger.models import Account, Category
from apps.users.models import Company


class BankAccount(models.Model):
    account_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    branch_name = models.CharField(max_length=250, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_accounts')
    ledger = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='bank_accounts')

    def save(self, *args, **kwargs):
        if not self.ledger:
            ledger = Account(name=self.account_number, company=self.company)
            try:
                ledger.category = Category.objects.get(name='Bank Accounts', parent__name='Assets',
                                                       company=self.company)
            except Category.DoesNotExist:
                pass
            ledger.code = 'P-' + str(self.account_number)
            ledger.save()
            self.ledger = ledger
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} : {}'.format(self.account_name, self.company.name)
