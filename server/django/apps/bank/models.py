import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError as RestValidationError

from apps.company.models import Company, CompanyBaseModel
from apps.ledger.models import (
    Account,
    JournalEntry,
    Party,
    TransactionModel,
    set_ledger_transactions,
)
from apps.ledger.models.base import Transaction
from awecount.libs import wGenerator


class BankAccount(CompanyBaseModel):
    is_wallet = models.BooleanField(default=False)
    account_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=150, blank=True, null=True)
    bank_name = models.CharField(max_length=250, blank=True, null=True)
    short_name = models.CharField(max_length=250, blank=True, null=True)
    branch_name = models.CharField(max_length=250, blank=True, null=True)
    next_cheque_no = models.CharField(blank=True, null=True, max_length=255)
    transaction_commission_percent = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
    )
    ledger = models.ForeignKey(
        Account,
        null=True,
        on_delete=models.SET_NULL,
        related_name="bank_accounts",
    )
    commission_account = models.ForeignKey(
        Account,
        null=True,
        on_delete=models.SET_NULL,
        related_name="wallet_accounts",
    )

    def save(self, *args, **kwargs):
        if self.is_wallet:
            if not self.bank_name:
                raise RestValidationError({"bank_name": ["Wallet name is required!"]})
        else:
            if not self.account_number:
                raise RestValidationError(
                    {"account_number": ["Account Number is required!"]}
                )
            if not self.next_cheque_no:
                raise RestValidationError(
                    {"next_cheque_no": ["Cheque No. can not be empty value!"]}
                )
            elif not self.next_cheque_no.isdigit():
                raise RestValidationError(
                    {"next_cheque_no": ["Cheque No. can only contain digits!"]}
                )
        super().save(*args, **kwargs)
        post_save = False
        acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
        if (
            self.is_wallet
            and self.transaction_commission_percent
            and not self.commission_account_id
        ):
            commission_account = Account(
                name=self.full_name + " Commission", company=self.company
            )
            commission_account.add_category(acc_cat_system_codes["Bank Charges"])
            commission_account.suggest_code(self)
            commission_account.save()
            self.commission_account = commission_account
            post_save = True
        if not self.ledger:
            ledger = Account(name=self.full_name, company=self.company)
            ledger.add_category(acc_cat_system_codes["Bank Accounts"])
            ledger.suggest_code(self)
            ledger.save()
            self.ledger = ledger
            post_save = True
        if post_save:
            self.save()

    def increase_cheque_no(self):
        leading_zeroes = len(self.next_cheque_no) - len(
            str(int(self.next_cheque_no) + 1)
        )
        self.next_cheque_no = "0" * leading_zeroes + str(int(self.next_cheque_no) + 1)
        self.save()

    @property
    def friendly_name(self):
        return self.short_name or self.bank_name

    @property
    def full_name(self):
        if self.account_number:
            return "{} ({})".format(
                self.short_name or self.bank_name, self.account_number
            )
        else:
            return "{}".format(self.short_name or self.bank_name)

    def __str__(self):
        return self.short_name or self.bank_name or self.account_number

    class Meta:
        ordering = ["-id"]


class ChequeDeposit(TransactionModel, CompanyBaseModel):
    STATUSES = (
        ("Draft", "Draft"),
        ("Issued", "Issued"),
        ("Cleared", "Cleared"),
        ("Cancelled", "Cancelled"),
    )
    voucher_no = models.PositiveIntegerField(blank=True, null=True, default=None)
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=20)
    date = models.DateField()
    clearing_date = models.DateField(blank=True, null=True)
    bank_account = models.ForeignKey(
        BankAccount, related_name="cheque_deposits", on_delete=models.CASCADE
    )
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    cheque_date = models.DateField(blank=True, null=True)
    drawee_bank = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    benefactor = models.ForeignKey(Account, on_delete=models.CASCADE)
    deposited_by = models.CharField(max_length=255, blank=True, null=True)
    narration = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # files = models.ManyToManyField(File, blank=True)

    def __str__(self):
        return str(self.date)

    def get_voucher_no(self):
        return self.voucher_no or self.id

    def apply_transactions(self):
        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        if not self.status == "Cleared":
            return
        entries = [
            ["dr", self.bank_account.ledger, self.amount],
            ["cr", self.benefactor, self.amount],
        ]
        set_ledger_transactions(self, self.date, *entries, clear=True)

    def cancel_transactions(self):
        if not self.status == "Cancelled":
            return
        JournalEntry.objects.filter(
            content_type__model="chequedeposit", object_id=self.id
        ).delete()

    def clear(self, handle_receipt=True):
        self.status = "Cleared"
        self.clearing_date = datetime.datetime.today()
        self.save()
        self.apply_transactions()
        if handle_receipt:
            for receipt in self.payment_receipts.all():
                receipt.clear(handle_cheque=False)

    def cancel(self, handle_receipt=True):
        self.status = "Cancelled"
        self.save()
        self.cancel_transactions()
        if handle_receipt:
            for receipt in self.payment_receipts.all():
                receipt.cancel(handle_cheque=False)


# class ChequeDepositRow(models.Model):
#     cheque_number = models.CharField(max_length=50)
#     cheque_date = models.DateField(default=timezone.now)
#     drawee_bank = models.CharField(max_length=255)
#     drawee_bank_address = models.CharField(max_length=255)
#     amount = models.DecimalField(max_digits=24, decimal_places=6, validators=[MinValueValidator(Decimal("0.000000"))])
#     cheque_deposit = models.ForeignKey(ChequeDeposit, related_name='rows', on_delete=models.CASCADE)
#
#     company_id_accessor = 'cheque_deposit__company_id'
#
#     def get_voucher_no(self):
#         return self.cheque_deposit_id


class ChequeIssue(CompanyBaseModel):
    STATUSES = (
        ("Issued", "Issued"),
        ("Cancelled", "Cancelled"),
    )
    cheque_no = models.CharField(max_length=100, null=True, blank=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT)
    date = models.DateField()
    party = models.ForeignKey(Party, on_delete=models.PROTECT, blank=True, null=True)
    issued_to = models.CharField(max_length=255, blank=True, null=True)
    dr_account = models.ForeignKey(
        Account,
        blank=True,
        null=True,
        related_name="cheque_issues",
        on_delete=models.SET_NULL,
    )
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=25)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk and self.bank_account_id:
            self.bank_account.increase_cheque_no()
        if self.party_id:
            self.dr_account = None
        else:
            if not self.issued_to:
                raise ValidationError("Party or Issued To is required.")
            if not self.dr_account:
                raise ValidationError("Dr Account is required.")

        super().save(*args, **kwargs)
        self.apply_transactions()

    def get_voucher_no(self):
        return self.cheque_no

    @property
    def voucher_no(self):
        return self.cheque_no

    def get_source_id(self):
        return self.id

    def __str__(self):
        return str(self.date)

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.amount)

    def apply_transactions(self):
        if self.status == "Issued":
            entries = [["cr", self.bank_account.ledger, self.amount]]
            if self.party_id:
                entries.append(["dr", self.party.supplier_account, self.amount])
            else:
                entries.append(["dr", self.dr_account, self.amount])
            set_ledger_transactions(self, self.date, *entries, clear=True)
        elif self.status == "Cancelled":
            self.cancel_transactions()

    def cancel_transactions(self):
        JournalEntry.objects.filter(
            content_type__model="chequeissue", object_id=self.id
        ).delete()

    def cancel(self):
        self.status = "Cancelled"
        self.save()
        self.cancel_transactions()


# class CashDeposit(models.Model):
#     STATUSES = (
#         ('Draft', 'Draft'),
#         ('Deposited', 'Deposited'),
#         ('Cancelled', 'Cancelled'),
#     )
#     bank_account = models.ForeignKey(BankAccount, blank=True, null=True, on_delete=models.PROTECT)
#     amount = models.FloatField()
#     benefactor = models.ForeignKey(Account, on_delete=models.CASCADE)
#     deposited_by = models.CharField(max_length=255, blank=True, null=True)
#     narration = models.TextField(null=True, blank=True)
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=20)
#     date = models.DateField()


class FundTransfer(TransactionModel, CompanyBaseModel):
    STATUSES = (
        ("Issued", "Issued"),
        ("Cancelled", "Cancelled"),
    )
    voucher_no = models.CharField(blank=True, null=True, max_length=50)
    date = models.DateField()
    from_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="fund_transfers_from"
    )
    to_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="fund_transfers_to"
    )
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    transaction_fee_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="charged_fund_transfers",
    )
    transaction_fee = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=25)
    narration = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES
        if acc_cat_system_codes["Bank Accounts"] not in [
            self.from_account.category.system_code,
            self.to_account.category.system_code,
        ]:
            raise ValidationError("One of the account needs to be a bank account.")
        if self.from_account_id == self.to_account_id:
            raise ValidationError("Transferring to the same account is not allowed.")
        if self.pk and not self.voucher_no:
            self.voucher_no = self.pk
        super().save(*args, **kwargs)
        if not self.voucher_no:
            self.voucher_no = self.pk
            super().save(update_fields=["voucher_no"])
        self.apply_transactions()

    def get_voucher_no(self):
        return self.voucher_no

    def get_source_id(self):
        return self.id

    def __str__(self):
        return str(self.date)

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.amount)

    def apply_transactions(self):
        if self.status == "Issued":
            entries = [["dr", self.to_account, self.amount]]
            cr_amount = self.amount
            if self.transaction_fee_account_id and self.transaction_fee:
                entries.append(
                    ["dr", self.transaction_fee_account, self.transaction_fee]
                )
                cr_amount += self.transaction_fee
            entries.append(["cr", self.from_account, cr_amount])
            set_ledger_transactions(self, self.date, *entries, clear=True)
        elif self.status == "Cancelled":
            self.cancel_transactions()

    def cancel_transactions(self):
        JournalEntry.objects.filter(
            content_type__model="fundtransfer", object_id=self.id
        ).delete()

    def cancel(self):
        self.status = "Cancelled"
        self.save()
        self.cancel_transactions()


class FundTransferTemplate(CompanyBaseModel):
    name = models.CharField(max_length=255)
    from_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="fund_transfers_from_template",
        blank=True,
        null=True,
    )
    to_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="fund_transfers_to_template",
        blank=True,
        null=True,
    )
    transaction_fee_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="charged_fund_transfers_template",
    )
    transaction_fee = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
        # return '{} -> {}'.format(str(self.from_account), str(self.to_account))


class BankCashDeposit(TransactionModel, CompanyBaseModel):
    STATUSES = (
        ("Cleared", "Cleared"),
        ("Cancelled", "Cancelled"),
    )
    voucher_no = models.IntegerField(blank=True, null=True, default=None)
    date = models.DateField()
    status = models.CharField(choices=STATUSES, default=STATUSES[0][0], max_length=25)
    bank_account = models.ForeignKey(
        BankAccount, related_name="bank_cash_deposits", on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    benefactor = models.ForeignKey(Account, on_delete=models.CASCADE)
    deposited_by = models.CharField(max_length=255, blank=True, null=True)
    narration = models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)

    def get_voucher_no(self):
        return self.voucher_no or self.id

    def apply_transactions(self):
        if self.status == "Cancelled":
            self.cancel_transactions()
            return
        entries = [
            ["dr", self.bank_account.ledger, self.amount],
            ["cr", self.benefactor, self.amount],
        ]
        set_ledger_transactions(self, self.date, *entries, clear=True)

    def cancel_transactions(self):
        if not self.status == "Cancelled":
            return
        JournalEntry.objects.filter(
            content_type__model="bankcashdeposit", object_id=self.id
        ).delete()

    def clear(self):
        self.status = "Cleared"
        self.clearing_date = datetime.datetime.today()
        self.save()
        self.apply_transactions()

    def cancel(self):
        self.status = "Cancelled"
        self.save()
        self.cancel_transactions()


BANK_RECONCILIATION_STATUS = (
    ("Reconciled", "Reconciled"),
    ("Matched", "Matched"),
    ("Unreconciled", "Unreconciled"),
)


class ReconciliationStatement(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="bank_reconciliation_statements"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="bank_reconciliation_statements"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name or str(self.start_date)


class ReconciliationRow(models.Model):
    status = models.CharField(
        choices=BANK_RECONCILIATION_STATUS,
        default=BANK_RECONCILIATION_STATUS[0][0],
        max_length=20,
    )
    date = models.DateField()
    dr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    cr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    balance = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    statement = models.ForeignKey(
        ReconciliationStatement, on_delete=models.CASCADE, related_name="rows"
    )
    # - if the amount is positive, it means the bank statement has more money than the ledger
    adjustment_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    def __str__(self):
        return str(self.date)

    @property
    def voucher_no(self):
        return self.id

    def apply_transactions(self, adjustment_account, date):
        if not self.adjustment_amount:
            return
        entries = []

        bank_account = self.statement.account

        adjustment_amount_absolute = abs(self.adjustment_amount)
        if self.adjustment_amount < 0:
            entries.append(("cr", bank_account, adjustment_amount_absolute))
            entries.append(("dr", adjustment_account, adjustment_amount_absolute))
        elif self.adjustment_amount > 0:
            entries.append(("dr", bank_account, adjustment_amount_absolute))
            entries.append(("cr", adjustment_account, adjustment_amount_absolute))
        set_ledger_transactions(self, date, *entries, clear=True)


class ReconciliationRowTransaction(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reconciliation_rows_transactions",
    )
    reconciliation_row = models.ForeignKey(
        ReconciliationRow,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    # To keep track of the last updated transaction
    transaction_last_updated_at = models.DateTimeField()
