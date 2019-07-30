from django.db import models

# Create your models here.
from django.utils import timezone

from apps.ledger.models import Account, Category
from apps.users.models import Company
from awecount.utils import get_next_voucher_no


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


class ChequeDeposit(models.Model):
    voucher_no = models.IntegerField()
    date = models.DateField()
    bank_account = models.ForeignKey(Account, related_name='cheque_deposits', on_delete=models.CASCADE)
    clearing_date = models.DateField(default=timezone.now)
    benefactor = models.ForeignKey(Account, on_delete=models.CASCADE)
    deposited_by = models.CharField(max_length=254, blank=True, null=True)
    narration = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # files = models.ManyToManyField(File, blank=True)

    def __init__(self, *args, **kwargs):
        super(ChequeDeposit, self).__init__(*args, **kwargs)
        if not self.pk and not self.voucher_no:
            self.voucher_no = get_next_voucher_no(ChequeDeposit, self.company_id)

    def __str__(self):
        return str(self.voucher_no) + ' : ' + str(self.deposited_by)

    def get_voucher_no(self):
        return self.id

    @property
    def total(self):
        grand_total = 0
        for obj in self.rows.all():
            total = obj.amount
            grand_total += total
        return grand_total

        # class Meta:
        #     unique_together = ('voucher_no', 'company')

# TODO drawee bank foreign key to Bank
class ChequeDepositRow(models.Model):
    cheque_number = models.CharField(max_length=50)
    cheque_date = models.DateField(default=timezone.now)
    drawee_bank = models.CharField(max_length=254)
    drawee_bank_address = models.CharField(max_length=254)
    amount = models.FloatField()
    cheque_deposit = models.ForeignKey(ChequeDeposit, related_name='rows', on_delete=models.CASCADE)

    def get_voucher_no(self):
        return self.cheque_deposit.id
