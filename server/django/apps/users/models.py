from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

from apps.users.signals import company_creation
from separatedvaluesfield.models import SeparatedValuesField

ORGANIZATION_TYPES = (
    ('sole_proprietorship', 'Sole Proprietorship'), ('partnership', 'Partnership'), ('corporation', 'Corporation'),
    ('non_profit', 'Non-profit'))


class FiscalYear(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.name

    def includes(self, date):
        return self.start <= date <= self.end


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    logo = models.ImageField(blank=True, null=True)
    contact_no = models.CharField(max_length=25)
    email = models.EmailField()
    organization_type = models.CharField(max_length=255, choices=ORGANIZATION_TYPES, default='sole_proprietorship')
    tax_registration_number = models.IntegerField(blank=True, null=True)
    force_preview_before_save = models.BooleanField(default=False)
    enable_sales_voucher_update = models.BooleanField(default=False)
    current_fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='companies')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Companies'

    def get_fiscal_years(self):
        # TODO Assign fiscal years to companies (m2m), return related fiscal years here 
        return sorted(FiscalYear.objects.all(), key=lambda fy: 999 if fy.id == self.current_fiscal_year_id else fy.id,
                      reverse=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        super(Company, self).save(*args, **kwargs)
        if created:
            company_creation.send(sender=None, company=self)


class UserManager(BaseUserManager):
    def create_user(self, email, full_name='', password=None, superuser=False):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=UserManager.normalize_email(email),
            full_name=full_name,
        )
        user.set_password(password)
        user.is_superuser = superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name='', password=None):
        return self.create_user(
            email,
            password=password,
            full_name=full_name,
            superuser=True
        )


# TODO Simplify
MODULES = (
    ('Dashboard', 'Dashboard'),
    ('ItemView', 'ItemView'),
    ('ItemCreate', 'ItemCreate'),
    ('ItemModify', 'ItemModify'),
    ('ItemDelete', 'ItemDelete'),
    ('UnitView', 'UnitView'),
    ('UnitCreate', 'UnitCreate'),
    ('UnitModify', 'UnitModify'),
    ('UnitDelete', 'UnitDelete'),
    ('PartyView', 'PartyView'),
    ('PartyCreate', 'PartyCreate'),
    ('PartyModify', 'PartyModify'),
    ('PartyDelete', 'PartyDelete'),
    ('AccountView', 'AccountView'),
    ('AccountCreate', 'AccountCreate'),
    ('AccountModify', 'AccountModify'),
    ('AccountDelete', 'AccountDelete'),
    ('TaxSchemeView', 'TaxSchemeView'),
    ('TaxSchemeCreate', 'TaxSchemeCreate'),
    ('TaxSchemeModify', 'TaxSchemeModify'),
    ('TaxSchemeDelete', 'TaxSchemeDelete'),
    ('SalesVoucherView', 'SalesVoucherView'),
    ('SalesVoucherCreate', 'SalesVoucherCreate'),
    ('SalesVoucherModify', 'SalesVoucherModify'),
    ('SalesVoucherIssuedModify', 'SalesVoucherIssuedModify'),
    ('SalesVoucherDelete', 'SalesVoucherDelete'),
    ('PurchaseVoucherView', 'PurchaseVoucherView'),
    ('PurchaseVoucherCreate', 'PurchaseVoucherCreate'),
    ('PurchaseVoucherModify', 'PurchaseVoucherModify'),
    ('PurchaseVoucherDelete', 'PurchaseVoucherDelete'),
    ('CreditNoteView', 'CreditNoteView'),
    ('CreditNoteCreate', 'CreditNoteCreate'),
    ('CreditNoteModify', 'CreditNoteModify'),
    ('CreditNoteDelete', 'CreditNoteDelete'),
    ('ChequeVoucherView', 'ChequeVoucherView'),
    ('ChequeVoucherCreate', 'ChequeVoucherCreate'),
    ('ChequeVoucherModify', 'ChequeVoucherModify'),
    ('ChequeVoucherDelete', 'ChequeVoucherDelete'),
    ('ChequeDepositView', 'ChequeDepositView'),
    ('ChequeDepositCreate', 'ChequeDepositCreate'),
    ('ChequeDepositModify', 'ChequeDepositModify'),
    ('ChequeDepositDelete', 'ChequeDepositDelete'),
    ('BankAccountView', 'BankAccountView'),
    ('BankAccountCreate', 'BankAccountCreate'),
    ('BankAccountModify', 'BankAccountModify'),
    ('BankAccountDelete', 'BankAccountDelete'),
    ('InvoiceDesignView', 'InvoiceDesignView'),
    ('InvoiceDesignCreate', 'InvoiceDesignCreate'),
    ('InvoiceDesignModify', 'InvoiceDesignModify'),
    ('CategoryView', 'CategoryView'),
    ('CategoryCreate', 'CategoryCreate'),
    ('CategoryModify', 'CategoryModify'),
    ('JournalVoucherView', 'JournalVoucherView'),
    ('JournalVoucherCreate', 'JournalVoucherCreate'),
    ('JournalVoucherModify', 'JournalVoucherModify'),
    ('BankBranchView', 'BankBranchView'),
    ('BankBranchCreate', 'BankBranchCreate'),
    ('BankBranchModify', 'BankBranchModify'),
    ('BankBranchDelete', 'BankBranchDelete'),
    ('InventoryCategoryView', 'InventoryCategoryView'),
    ('InventoryCategoryCreate', 'InventoryCategoryCreate'),
    ('InventoryCategoryModify', 'InventoryCategoryModify'),
    ('InventoryCategoryDelete', 'InventoryCategoryDelete'),
    ('BrandView', 'BrandView'),
    ('BrandCreate', 'BrandCreate'),
    ('BrandModify', 'BrandModify'),
    ('BrandDelete', 'BrandDelete'),
    ('SalesDiscountView', 'SalesDiscountView'),
    ('SalesDiscountCreate', 'SalesDiscountCreate'),
    ('SalesDiscountModify', 'SalesDiscountModify'),
    ('SalesDiscountDelete', 'SalesDiscountDelete'),
    ('PurchaseDiscountView', 'PurchaseDiscountView'),
    ('PurchaseDiscountCreate', 'PurchaseDiscountCreate'),
    ('PurchaseDiscountModify', 'PurchaseDiscountModify'),
    ('PurchaseDiscountDelete', 'PurchaseDiscountDelete'),
    ('InventoryAccountView', 'InventoryAccountView'),
    ('InventoryAccountCreate', 'InventoryAccountCreate'),
    ('InventoryAccountModify', 'InventoryAccountModify'),
    ('InventoryAccountDelete', 'InventoryAccountDelete'),
    ('BookView', 'BookView'),
    ('BookCreate', 'BookCreate'),
    ('BookModify', 'BookModify'),
    ('LogEntryView', 'LogEntryView'),
)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    modules = SeparatedValuesField(choices=MODULES, max_length=2000, blank=True, null=True, token=',')

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='users')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', ]

    objects = UserManager()

    def __str__(self):
        return self.full_name

    def is_staff(self):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
