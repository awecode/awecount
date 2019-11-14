from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.ledger.models import Account, Party, set_ledger_transactions, JournalEntry
from apps.users.models import Company, User
from awecount.utils import wGenerator


class BankAccount(models.Model):
    account_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    branch_name = models.CharField(max_length=250, blank=True, null=True)
    next_cheque_no = models.CharField(blank=True, null=True, max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bank_accounts')
    ledger = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='bank_accounts')

    def save(self, *args, **kwargs):
        if not self.next_cheque_no or not self.next_cheque_no.isdigit():
            raise ValidationError('Cheque No. can only contain digits.')
        super().save(*args, **kwargs)
        if not self.ledger:
            ledger = Account(name=self.full_name, company=self.company)
            ledger.add_category('Bank Accounts')
            ledger.suggest_code(self)
            ledger.save()
            self.ledger = ledger
            self.save()

    def increase_cheque_no(self):
        leading_zeroes = len(self.next_cheque_no) - len(str(int(self.next_cheque_no) + 1))
        self.next_cheque_no = '0' * leading_zeroes + str(int(self.next_cheque_no) + 1)
        self.save()

    @property
    def friendly_name(self):
        return self.short_name or self.bank_name

    @property
    def full_name(self):
        return '{} ({})'.format(self.short_name or self.bank_name, self.account_number)

    def __str__(self):
        return self.short_name or self.bank_name or self.account_number


class ChequeDeposit(models.Model):
    STATUSES = (
        ('Draft', 'Draft'),
        ('Issued', 'Issued'),
        ('Cleared', 'Cleared'),
        ('Cancelled', 'Cancelled'),
    )
    voucher_no = models.IntegerField(blank=True, null=True, default=None)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=20)
    date = models.DateField()
    clearing_date = models.DateField(blank=True, null=True)
    bank_account = models.ForeignKey(BankAccount, related_name='cheque_deposits', on_delete=models.CASCADE)
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    cheque_date = models.DateField(blank=True, null=True)
    drawee_bank = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField()
    benefactor = models.ForeignKey(Account, on_delete=models.CASCADE)
    deposited_by = models.CharField(max_length=255, blank=True, null=True)
    narration = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # files = models.ManyToManyField(File, blank=True)
    # TODO Find payment and set as cleared for cleared cheque deposits

    def __str__(self):
        return str(self.date)

    def get_voucher_no(self):
        return self.voucher_no or self.id

    def apply_transactions(self):
        if self.status == 'Cancelled':
            self.cancel_transactions()
            return
        if not self.status == 'Cleared':
            return
        entries = [['dr', self.bank_account.ledger, self.amount], ['cr', self.benefactor, self.amount]]
        set_ledger_transactions(self, self.date, *entries, clear=True)

    def cancel_transactions(self):
        if not self.status == 'Cancelled':
            return
        JournalEntry.objects.filter(content_type__model='chequedeposit', object_id=self.id).delete()


# class ChequeDepositRow(models.Model):
#     cheque_number = models.CharField(max_length=50)
#     cheque_date = models.DateField(default=timezone.now)
#     drawee_bank = models.CharField(max_length=255)
#     drawee_bank_address = models.CharField(max_length=255)
#     amount = models.FloatField()
#     cheque_deposit = models.ForeignKey(ChequeDeposit, related_name='rows', on_delete=models.CASCADE)
# 
#     company_id_accessor = 'cheque_deposit__company_id'
# 
#     def get_voucher_no(self):
#         return self.cheque_deposit_id


class ChequeIssue(models.Model):
    cheque_no = models.CharField(max_length=100, null=True, blank=True)
    bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.PROTECT)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    dr_account = models.ForeignKey(Account, blank=True, null=True, related_name='cheque_issues', on_delete=models.SET_NULL)
    amount = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.bank_account.increase_cheque_no()
        super(ChequeIssue, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date)

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.amount)
