from datetime import datetime, timedelta
from decimal import Decimal

from dateutil.utils import today
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, F, ProtectedError, Q, Sum, Value, When
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from rest_framework.exceptions import ValidationError as RestValidationError

from apps.company.models import Company, CompanyBaseModel, FiscalYear
from awecount.libs import decimalize, none_for_zero, zero_for_none
from awecount.libs.exception import BadOperation

acc_system_codes = settings.ACCOUNT_SYSTEM_CODES
acc_cat_system_codes = settings.ACCOUNT_CATEGORY_SYSTEM_CODES


class Category(MPTTModel, CompanyBaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    parent = TreeForeignKey(
        "self", null=True, related_name="children", on_delete=models.SET_NULL
    )
    code = models.CharField(max_length=20, null=True, blank=True)
    system_code = models.CharField(max_length=20, null=True, blank=True)
    default = models.BooleanField(default=False, editable=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="ledger_categories"
    )

    def set_parent(self, category):
        if type(category) == str:
            parent_instance = Category.objects.get(
                system_code=category, company=self.company
            )
        else:
            parent_instance = category
        self.parent = parent_instance

    def suggest_code(self, obj, prefix=None):
        cat_code = self.parent.code
        if prefix:
            cat_code = cat_code + "-" + str(prefix)
        if type(obj) in [int, str]:
            self.code = "{}-{}".format(cat_code, obj)
        elif hasattr(obj, "id"):
            self.code = "{}-{}".format(cat_code, obj.id)
        elif hasattr(obj, "code"):
            self.code = "{}-{}".format(cat_code, obj.code)
        return self.code

    ROOT = (
        ("Assets", "A"),
        ("Liabilities", "L"),
        ("Income", "I"),
        ("Expenses", "E"),
        ("Equity", "Q"),
        ("Opening Balance Difference", "O"),
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.default and not self.parent:
            raise RestValidationError({"parent": ["Requires Parent"]})
        super().save(*args, **kwargs)

    @classmethod
    def get(cls, name, company):
        return cls.objects.get(default=True, company=company, name=name)

    def get_data(self):
        node = Node(self)
        return node.get_data()

    def get_descendant_accounts(self):
        ledgers = self.accounts.all()
        for descendant in self.get_descendants():
            ledgers = ledgers | descendant.accounts.all()
        return ledgers

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = (
            ("code", "company"),
            ("system_code", "company"),
        )


class Account(CompanyBaseModel):
    code = models.CharField(max_length=50, blank=True, null=True)
    system_code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255)
    # current_dr and current_cr may not always be exact
    current_dr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    current_cr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        Category, related_name="accounts", on_delete=models.PROTECT
    )
    tax_rate = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    opening_dr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    opening_cr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    order = models.PositiveIntegerField(default=0)
    default = models.BooleanField(default=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="ledger_accounts"
    )
    source = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="source_accounts",
        on_delete=models.SET_NULL,
    )

    def get_absolute_url(self):
        # return '/ledger/' + str(self.id)
        return "url"

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        return zero_for_none(self.current_dr) - zero_for_none(self.current_cr)

    def get_day_opening(self, before_date=None):
        if not before_date:
            before_date = today()
        tr = Transaction.objects.filter(
            account=self, journal_entry__date__lte=before_date
        ).aggregate(dr=Sum("dr_amount"), cr=Sum("cr_amount"))
        return (tr.get("dr") or 0) - (tr.get("cr") or 0)

    def get_day_closing(self, until_date=None):
        if not until_date:
            until_date = today()
        tr = Transaction.objects.filter(
            account=self, journal_entry__date__lte=until_date
        ).aggregate(dr=Sum("dr_amount"), cr=Sum("cr_amount"))
        return (tr.get("dr") or 0) - (tr.get("cr") or 0)

    def add_category(self, category):
        category_instance = Category.objects.get(
            system_code=category, company=self.company
        )
        self.category = category_instance

    def get_all_categories(self):
        return self.category.get_ancestors(include_self=True)

    categories = property(get_all_categories)

    def get_cr_amount(self, day):
        transactions = Transaction.objects.filter(
            journal_entry__date__lt=day, account=self
        ).order_by("-journal_entry__id", "-journal_entry__date")[:1]
        if len(transactions) > 0:
            return transactions[0].current_cr
        return 0

    def get_dr_amount(self, day):
        transactions = Transaction.objects.filter(
            journal_entry__date__lt=day, account=self
        ).order_by("-journal_entry__id", "-journal_entry__date")[:1]
        if len(transactions) > 0:
            return transactions[0].current_dr
        return 0

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     super().save()

    # def save(self, *args, **kwargs):
    #     queryset = Account.objects.all()
    #     original_name = self.name
    #     nxt = 2
    #     if not self.pk:
    #         while queryset.filter(**{'name': self.name, 'fy': self.fy}):
    #             self.name = original_name
    #             end = '%s%s' % ('-', nxt)
    #             if len(self.name) + len(end) > 100:
    #                 self.name = self.name[:100 - len(end)]
    #             self.name = '%s%s' % (self.name, end)
    #             nxt += 1
    #     return super(Account, self).save(*args, **kwargs)

    def suggest_code(self, obj, prefix=None):
        cat_code = self.category.code
        if prefix:
            cat_code = cat_code + "-" + str(prefix)
        if type(obj) in [int, str]:
            self.code = "{}-{}".format(cat_code, obj)
        elif hasattr(obj, "id"):
            self.code = "{}-{}".format(cat_code, obj.id)
        elif hasattr(obj, "code"):
            self.code = "{}-{}".format(cat_code, obj.code)
        return self.code

    def __str__(self):
        return self.name

    @classmethod
    def get_creditable_accounts(self):
        return Account.objects.filter(
            Q(system_code=acc_system_codes["Cash"])
            | Q(category__system_code=acc_cat_system_codes["Bank Accounts"])
            | Q(category__system_code=acc_cat_system_codes["Customers"])
        )

    @classmethod
    def get_payment_accounts(self):
        return Account.objects.filter(
            Q(system_code=acc_system_codes["Cash"])
            | Q(category__system_code=acc_cat_system_codes["Bank Accounts"])
        )

    @property
    def amounts(self):
        return Transaction.objects.filter(account=self).aggregate(
            dr=Sum("dr_amount"), cr=Sum("cr_amount")
        )

    @property
    def transaction_amounts(self):
        return 0
        # return self.transactions.aggregate(dr=Sum('dr_amount'), cr=Sum('cr_amount'))

    class Meta:
        unique_together = (
            ("code", "company"),
            ("system_code", "company"),
        )
        # ordering = ('order',)
        ordering = ["name"]


class Party(CompanyBaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tax_identification_number = models.CharField(max_length=255, blank=True, null=True)
    supplier_account = models.OneToOneField(
        Account, null=True, related_name="supplier_detail", on_delete=models.SET_NULL
    )
    customer_account = models.OneToOneField(
        Account, null=True, related_name="customer_detail", on_delete=models.SET_NULL
    )

    aliases = ArrayField(models.CharField(max_length=255), blank=True, default=list)

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="parties"
    )

    def can_be_deleted(self):
        # Allow party to be deleted only if no transactions exist
        return Party.objects.filter(
            supplier_account__transactions__isnull=True,
            customer_account__transactions__isnull=True,
            company_id=self.company_id,
            id=self.id,
        ).exists()

    def delete(self, *args, **kwargs):
        # Allow party to be deleted only if no transactions exist
        if not Party.objects.filter(
            supplier_account__transactions__isnull=True,
            customer_account__transactions__isnull=True,
            company_id=self.company_id,
            id=self.id,
        ).exists():
            raise BadOperation(
                "This party has transactions and therefore can not be deleted."
            )
        try:
            super().delete(*args, **kwargs)
        except ProtectedError as exc:
            raise BadOperation(str(exc))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Parties"
        unique_together = ("company", "tax_identification_number")

    def save(self, *args, **kwargs):
        self.validate_unique()
        post_save = False
        if self.pk is None:
            post_save = True
        super().save(*args, **kwargs)
        if post_save:
            if not self.customer_account_id:
                customer_account = Account(
                    name=self.name + " (Receivable)", company=self.company
                )
                customer_account.add_category(acc_cat_system_codes["Customers"])
                customer_account.suggest_code(self)
                customer_account.save()
                self.customer_account = customer_account
            if not self.supplier_account_id:
                supplier_account = Account(
                    name=self.name + " (Payable)", company=self.company
                )
                supplier_account.add_category(acc_cat_system_codes["Suppliers"])
                supplier_account.suggest_code(self)
                supplier_account.save()
                self.supplier_account = supplier_account
            self.save()


class PartyRepresentative(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    party = models.ForeignKey(
        Party, on_delete=models.CASCADE, related_name="representative"
    )

    company_id_accessor = "party__company_id"

    def __str__(self):
        return self.name or "-"


class Node(object):
    def __init__(self, model, parent=None, depth=0):
        self.children = []
        self.model = model
        self.name = self.model.name
        self.type = self.model.__class__.__name__
        self.dr = 0
        self.cr = 0
        self.url = None
        self.depth = depth
        self.parent = parent
        if self.type == "Category":
            for child in self.model.children.all():
                self.add_child(Node(child, parent=self, depth=self.depth + 1))
            for account in self.model.accounts.all():
                self.add_child(Node(account, parent=self, depth=self.depth + 1))
        if self.type == "Account":
            self.dr = self.model.current, "company_dr or 0"
            self.cr = self.model.current_cr or 0
            self.url = self.model.get_absolute_url()
        if self.parent:
            self.parent.dr += self.dr
            self.parent.cr += self.cr

    def add_child(self, obj):
        self.children.append(obj.get_data())

    def get_data(self):
        data = {
            "name": self.name,
            "type": self.type,
            "dr": self.dr,
            "cr": self.cr,
            "nodes": self.children,
            "depth": self.depth,
            "url": self.url,
        }
        return data

    def __str__(self):
        return self.name


TRANSACTION_TYPES = (
    ("Regular", "Regular"),
    ("Opening", "Opening"),
    ("Closing", "Closing"),
)


class JournalEntry(models.Model):
    date = models.DateField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="journal_entries"
    )
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey("content_type", "object_id")
    type = models.CharField(
        TRANSACTION_TYPES, max_length=25, default=TRANSACTION_TYPES[0][0]
    )
    source_voucher_no = models.CharField(max_length=50, blank=True, null=True)
    source_voucher_id = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return (
            str(self.content_type)
            + ": "
            + str(self.object_id)
            + " ["
            + str(self.date)
            + "]"
        )

    @staticmethod
    def get_for(source):
        try:
            return JournalEntry.objects.get(
                content_type=ContentType.objects.get_for_model(source),
                object_id=source.id,
            )
        except JournalEntry.DoesNotExist:
            return None

    class Meta:
        verbose_name_plural = "Journal Entries"


class Transaction(CompanyBaseModel):
    account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="transactions"
    )
    dr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    cr_amount = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    current_dr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    current_cr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    journal_entry = models.ForeignKey(
        JournalEntry, related_name="transactions", on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="transactions", null=True
    )
    type = models.CharField(
        choices=TRANSACTION_TYPES, max_length=25, default=TRANSACTION_TYPES[0][0]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def get_amount(self):
        return self.dr_amount - self.cr_amount

    def get_balance(self):
        return zero_for_none(self.current_dr) - zero_for_none(self.current_cr)

    def __str__(self):
        return (
            str(self.account)
            + " ["
            + str(self.dr_amount)
            + " / "
            + str(self.cr_amount)
            + "]"
        )


def alter(account, date, dr_difference, cr_difference):
    Transaction.objects.filter(journal_entry__date__gt=date, account=account).update(
        current_dr=Case(
            When(current_dr__isnull=True, then=Value(zero_for_none(dr_difference))),
            default=F("current_dr") + Value(zero_for_none(dr_difference)),
        ),
        current_cr=Case(
            When(current_cr__isnull=True, then=Value(zero_for_none(cr_difference))),
            default=F("current_cr") + Value(zero_for_none(cr_difference)),
        ),
    )


def set_transactions(submodel, date, *entries, check=True, clear=True):
    """

    :param date: datetime object
    :param submodel: source model
    :param check: boolean - checks for debit/credit mismatch
    :type clear: object
    Clears all transactions not accounted here
    """
    # TODO: Security: Validate company. At least make sure all accounts are from the same company. Also validate against the source or submodel company.
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")

    content_type = ContentType.objects.get_for_model(submodel)

    created = False
    try:
        journal_entry = JournalEntry.objects.get(
            content_type=content_type, object_id=submodel.id
        )
    except JournalEntry.DoesNotExist:
        if hasattr(submodel, "voucher_id"):
            voucher_id = submodel.voucher_id
            voucher_no = submodel.voucher.voucher_no
        else:
            voucher_id = submodel.id
            voucher_no = submodel.voucher_no

        journal_entry = JournalEntry(
            content_type=content_type,
            object_id=submodel.id,
            date=date,
            source_voucher_id=voucher_id,
            source_voucher_no=voucher_no,
        )
        journal_entry.save()
        created = True

    dr_total = 0
    cr_total = 0
    all_accounts = []
    all_transaction_ids = []
    for arg in entries:
        # transaction = Transaction(account=arg[1], dr_amount=arg[2])
        matches = (
            journal_entry.transactions.filter(account=arg[1]) if not created else []
        )
        # with localcontext() as ctx:
        #     ctx.rounding = ROUND_HALF_UP
        #     val = round(decimalize(arg[2]), 2)
        val = decimalize(str(arg[2]))
        # val = arg[2]
        all_accounts.append(arg[1])
        if not matches:
            if arg[1] is None:
                raise ValidationError(
                    "Cannot create {} transaction {} when account does not exist!".format(
                        arg[0], arg[2]
                    )
                )
            transaction = Transaction(account=arg[1], company=arg[1].company)
            if arg[0] == "dr":
                transaction.dr_amount = val
                transaction.cr_amount = None
                transaction.account.current_dr = none_for_zero(
                    decimalize(transaction.account.current_dr)
                    + decimalize(transaction.dr_amount)
                )
                alter(arg[1], date, val, 0)
                dr_total += val
            if arg[0] == "cr":
                transaction.cr_amount = val
                transaction.dr_amount = None
                transaction.account.current_cr = none_for_zero(
                    decimalize(transaction.account.current_cr)
                    + decimalize(transaction.cr_amount)
                )
                alter(arg[1], date, 0, val)
                cr_total += val

            transaction.current_dr = none_for_zero(
                round(
                    decimalize(
                        transaction.account.get_dr_amount(date + timedelta(days=1))
                    )
                    + decimalize(transaction.dr_amount),
                    2,
                )
            )
            transaction.current_cr = none_for_zero(
                round(
                    decimalize(
                        transaction.account.get_cr_amount(date + timedelta(days=1))
                    )
                    + decimalize(transaction.cr_amount),
                    2,
                )
            )
        else:
            transaction = matches[0]
            transaction.account = arg[1]

            # cancel out existing dr_amount and cr_amount from current_dr and current_cr
            # if transaction.dr_amount:
            #     transaction.current_dr -= transaction.dr_amount
            #     transaction.account.current_dr -= transaction.dr_amount
            #
            # if transaction.cr_amount:
            #     transaction.current_cr -= transaction.cr_amount
            #     transaction.account.current_cr -= transaction.cr_amount

            # save new dr_amount and add it to current_dr/cr

            if arg[0] == "dr":
                dr_difference = val - decimalize(transaction.dr_amount)
                cr_difference = decimalize(transaction.cr_amount) * -1
                alter(
                    arg[1], transaction.journal_entry.date, dr_difference, cr_difference
                )
                transaction.dr_amount = val
                transaction.cr_amount = None
                dr_total += transaction.dr_amount
            else:
                cr_difference = val - decimalize(transaction.cr_amount)
                dr_difference = decimalize(transaction.dr_amount) * -1
                alter(
                    arg[1], transaction.journal_entry.date, dr_difference, cr_difference
                )
                transaction.cr_amount = val
                transaction.dr_amount = None
                cr_total += transaction.cr_amount

            transaction.current_dr = none_for_zero(
                decimalize(transaction.current_dr) + dr_difference
            )
            transaction.current_cr = none_for_zero(
                decimalize(transaction.current_cr) + cr_difference
            )
            transaction.account.current_dr = none_for_zero(
                decimalize(transaction.account.current_dr) + dr_difference
            )
            transaction.account.current_cr = none_for_zero(
                decimalize(transaction.account.current_cr) + cr_difference
            )

        # the following code lies outside if,else block, inside for loop
        transaction.account.save()
        # new transactions if any are saved into db by following code
        try:
            journal_entry.transactions.add(transaction, bulk=False)
        except TypeError:  # for Django <1.9
            journal_entry.transactions.add(transaction)
        all_transaction_ids.append(transaction.id)

    # if date is updated on source calling set_transactions, update date on JE
    if journal_entry.date != date:
        journal_entry.date = date
        journal_entry.save()

    if clear:
        obsolete_transactions = journal_entry.transactions.exclude(
            id__in=all_transaction_ids
        )
        obsolete_transactions.delete()
    if check and round(dr_total, 2) != round(cr_total, 2):
        error_msg = "Dr/Cr mismatch from {0}, ID: {1}, Dr: {2}, Cr: {3}".format(
            str(submodel), submodel.id, dr_total, cr_total
        )
        # mail_admins('Dr/Cr mismatch!', error_msg)
        print(entries)
        raise RuntimeError(error_msg)


# @receiver(pre_delete, sender=Transaction)
# def _transaction_delete(sender, instance, **kwargs):
#     transaction = instance
#     if transaction.dr_amount:
#         transaction.account.current_dr -= transaction.dr_amount
#
#     if transaction.cr_amount:
#         transaction.account.current_cr -= transaction.cr_amount
#
#     alter(transaction.account, transaction.journal_entry.date, float(zero_for_none(transaction.dr_amount)) * -1,
#           float(zero_for_none(transaction.cr_amount)) * -1)
#
#     transaction.account.save()


def delete_rows(rows, model):
    for row in rows:
        if row.get("id"):
            instance = model.objects.get(id=row.get("id"))
            try:
                JournalEntry.objects.get(
                    content_type=ContentType.objects.get_for_model(model),
                    object_id=instance.id,
                ).delete()
            except:
                pass
            instance.delete()

def get_account(request_or_company, system_code):
    if not request_or_company.__class__.__name__ == "Company":
        company = request_or_company.company
    else:
        company = request_or_company
    return Account.objects.get(system_code=system_code, company=company)


class TransactionModel(models.Model):
    def get_voucher_no(self):
        if hasattr(self, "voucher_no"):
            return self.voucher_no
        if hasattr(self, "voucher"):
            if hasattr(self.voucher, "voucher_no"):
                return self.voucher.voucher_no
            else:
                return self.voucher_id
        return self.id

    def get_source_id(self):
        if hasattr(self, "voucher_id"):
            return self.voucher_id
        return self.id

    def journal_entries(self, additional_kwargs=None):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = JournalEntry.objects.filter(content_type__app_label=app_label)
        if hasattr(self, "rows"):
            row_ids = self.rows.values_list("id", flat=True)
            if additional_kwargs:
                qs = qs.filter(
                    Q(content_type__model=model + "row", object_id__in=row_ids)
                    | Q(content_type__model=model, object_id=self.id)
                    | Q(**additional_kwargs)
                )
            else:
                qs = qs.filter(
                    Q(content_type__model=model + "row", object_id__in=row_ids)
                    | Q(content_type__model=model, object_id=self.id)
                )
        else:
            qs = qs.filter(content_type__model=model, object_id=self.id)
        return qs

    def transactions(self):
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        qs = Transaction.objects.filter(
            journal_entry__content_type__app_label=app_label
        )
        if hasattr(self, "rows"):
            row_ids = self.rows.values_list("id", flat=True)
            qs = qs.filter(
                Q(
                    journal_entry__content_type__model=model + "row",
                    journal_entry__object_id__in=row_ids,
                )
                | Q(
                    journal_entry__content_type__model=model,
                    journal_entry__object_id=self.id,
                )
            )
        else:
            qs = qs.filter(
                journal_entry__content_type__model=model,
                journal_entry__object_id=self.id,
            )
        return qs

    class Meta:
        abstract = True


set_ledger_transactions = set_transactions


class TransactionCharge(CompanyBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    account = models.ForeignKey(
        Account,
        related_name="transaction_charges",
        on_delete=models.CASCADE,
        blank=True,
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.account_id:
            expense_account = Account(name=self.name, company=self.company)
            expense_account.add_category(acc_cat_system_codes["Indirect Expenses"])
            expense_account.suggest_code(self)
            expense_account.save()
            self.account = expense_account
        super().save(*args, **kwargs)


class AccountOpeningBalance(CompanyBaseModel):
    account = models.ForeignKey(
        Account,
        related_name="account_opening_balances",
        on_delete=models.CASCADE,
    )
    opening_dr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    opening_cr = models.DecimalField(
        max_digits=24,
        decimal_places=6,
        default=Decimal("0.000000"),
        validators=[MinValueValidator(Decimal("0.000000"))],
    )
    fiscal_year = models.ForeignKey(
        FiscalYear,
        related_name="account_opening_balances",
        on_delete=models.CASCADE,
    )
    company = models.ForeignKey(
        Company,
        related_name="account_opening_balances",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.opening_dr and self.opening_cr:
            raise ValidationError("Can't have both opening dr and cr.")
        if not self.opening_dr and not self.opening_cr:
            raise ValidationError("Either opening dr or cr is required.")
        if not self.fiscal_year_id:
            self.fiscal_year_id = self.company.current_fiscal_year_id
        super().save(*args, **kwargs)
        # self.account.opening_dr = self.opening_dr
        # self.account.opening_cr = self.opening_cr
        # self.account.save()
        opening_balance_difference = Account.objects.get(
            company=self.company,
            system_code=acc_system_codes["Opening Balance Difference"],
        )
        dr_entries = []
        cr_entries = []
        if self.opening_dr:
            dr_entries.append(["dr", self.account, self.opening_dr])
            dr_entries.append(["cr", opening_balance_difference, self.opening_dr])
            set_ledger_transactions(
                self, self.fiscal_year.previous_day, *dr_entries, check=True, clear=True
            )
        else:
            cr_entries.append(["cr", self.account, self.opening_cr])
            cr_entries.append(["dr", opening_balance_difference, self.opening_cr])
            set_ledger_transactions(
                self, self.fiscal_year.previous_day, *cr_entries, check=True, clear=True
            )

    def __str__(self):
        return self.account.name

    def get_voucher_no(self):
        return self.pk

    @property
    def voucher_no(self):
        return self.pk

    def get_source_id(self):
        return self.pk

    class Meta:
        unique_together = ("company", "fiscal_year", "account")


CLOSING_STATUSES = (
    ("Pending", "Pending"),
    ("Closed", "Closed"),
)


class AccountClosing(CompanyBaseModel):
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="account_closings"
    )
    fiscal_period = models.ForeignKey(FiscalYear, on_delete=models.PROTECT)
    status = models.CharField(
        choices=CLOSING_STATUSES, max_length=50, default=CLOSING_STATUSES[0][0]
    )
    journal_entry = models.ForeignKey(
        JournalEntry,
        related_name="account_closings",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    key = "AccountClosing"

    def get_source_id(self):
        return self.id

    def __str__(self):
        return "{}-{}".format(str(self.company), str(self.fiscal_period))

    def close(self):
        company = self.company
        date = self.fiscal_period.end_date
        pl_account = Account.objects.get(
            company=company, system_code=acc_system_codes["Profit and Loss Account"]
        )

        income_category = Category.objects.get(
            system_code=acc_cat_system_codes["Income"],
            company=company,
            parent__isnull=True,
        )
        income_accounts = Account.objects.filter(
            category__in=income_category.get_descendants(include_self=True)
        )

        expenses_category = Category.objects.get(
            system_code=acc_cat_system_codes["Expenses"],
            company=company,
            parent__isnull=True,
        )
        expenses_accounts = Account.objects.filter(
            category__in=expenses_category.get_descendants(include_self=True)
        )

        journal_entry = JournalEntry.objects.create(
            date=date,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            type="Closing",
        )
        jeid = journal_entry.id

        transactions = []

        total_income_amount = 0
        for income_account in income_accounts:
            income_amount = income_account.get_day_closing(until_date=date)
            # Amount is usually negative for Income
            income_amount = -1 * income_amount
            total_income_amount += income_amount
            # TODO What if amount is positive?
            if income_amount:
                transaction = Transaction(
                    account=income_account,
                    dr_amount=income_amount,
                    type="Closing",
                    journal_entry_id=jeid,
                    company_id=company.id,
                )
                transactions.append(transaction)

        total_expense_amount = 0
        for expense_account in expenses_accounts:
            expense_amount = expense_account.get_day_closing(until_date=date)
            # Amount is usually positive for Expense
            # TODO What if amount is negative?
            total_expense_amount += expense_amount

            if expense_amount:
                transaction = Transaction(
                    account=expense_account,
                    cr_amount=expense_amount,
                    type="Closing",
                    journal_entry_id=jeid,
                    company_id=company.id,
                )
                transactions.append(transaction)

        diff = total_income_amount - total_expense_amount

        if diff > 0:
            pl_transaction = Transaction(
                account=pl_account,
                journal_entry_id=jeid,
                company_id=company.id,
                cr_amount=diff,
                type="Closing",
            )
        else:
            pl_transaction = Transaction(
                account=pl_account,
                journal_entry_id=jeid,
                company_id=company.id,
                dr_amount=-1 * diff,
                type="Closing",
            )

        transactions.append(pl_transaction)

        Transaction.objects.bulk_create(transactions)
        self.journal_entry = journal_entry
        self.status = "Closed"
        self.save()
