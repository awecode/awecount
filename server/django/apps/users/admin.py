from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, UserChangeForm as DjangoUserChangeForm, \
    UserCreationForm as DjangoUserCreationForm
from django.db import IntegrityError
import requests

from apps.ledger.models import handle_company_creation
from apps.product.models import Unit, Category as InventoryCategory, Item, Brand
from apps.tax.models import TaxScheme
from .models import User, Company, Role, FiscalYear, AccessKey
from django import forms

admin.site.unregister(Group)

admin.site.site_header = "Awecount"
admin.site.site_title = "Awecount Admin Portal"
admin.site.index_title = "Welcome to Awecount"


def create_company_defaults(modeladmin, request, queryset):
    for company in queryset:
        handle_company_creation(modeladmin, company=company)


create_company_defaults.short_description = "Create company defaults"


class UserCreationForm(DjangoUserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    form = UserChangeForm
    add_form = UserCreationForm
    filter_horizontal = ()
    list_display_links = ('id', 'full_name', 'email', 'date_joined',)
    list_display = ('id', 'full_name', 'email', 'date_joined', 'company', 'is_superuser',)
    list_filter = ('is_superuser',)
    fieldsets = ((None,
                  {'fields': ('full_name',
                              'email',
                              'password',
                              'date_joined',
                              'last_login',
                              'company',
                              'roles',
                              'is_superuser',)}),
                 )
    add_fieldsets = ((None,
                      {'fields': ('full_name',
                                  'email',
                                  'password1',
                                  'password2',
                                  'company',
                                  )}),
                     )
    search_fields = ('full_name', 'email', 'company', 'is_superuser',)
    readonly_fields = ('is_superuser', 'date_joined', 'last_login',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)


def setup_nepali_tax_schemes(modeladmin, request, queryset):
    for company in queryset:
        try:
            tax_schemes = TaxScheme.setup_nepali_tax_schemes(company)
            messages.success(request, '{} tax scheme(s) created!'.format(len(tax_schemes)))
        except IntegrityError:
            messages.error(request, 'One or more tax schemes already exist!')


setup_nepali_tax_schemes.short_description = "Setup Nepali Tax Schemes"


def setup_basic_units(modeladmin, request, queryset):
    for company in queryset:
        try:
            units = Unit.create_default_units(company)
            messages.success(request, '{} unit(s) created!'.format(len(units)))
        except IntegrityError:
            messages.error(request, 'One or more units already exist!')


setup_basic_units.short_description = "Setup Basic Units"


def create_book_category(modeladmin, request, queryset):
    for company in queryset:
        unit, __ = Unit.objects.get_or_create(short_name='pcs', company=company, defaults={'name': 'Pieces'})
        tax, __ = TaxScheme.objects.get_or_create(short_name='Taxless', company=company,
                                                  defaults={'name': 'Taxless', 'rate': 0})
        extra_fields = [
            {"name": "nepali_title", "type": "Text", "enable_search": True},
            {"name": "english_subtitle", "type": "Text", "enable_search": False},
            {"name": "nepali_subtitle", "type": "Text", "enable_search": False},
            {"name": "english_description", "type": "Text", "enable_search": False},
            {"name": "nepali_description", "type": "Text", "enable_search": False},
            {"name": "genre", "type": "Choices", "enable_search": False},
            {"name": "authors", "type": "Text", "enable_search": True},
            {"name": "pages", "type": "Text", "enable_search": False},
            {"name": "format", "type": "Choices", "enable_search": False},
            {"name": "language", "type": "Choices", "enable_search": False},
            {"name": "edition", "type": "Choices", "enable_search": False},
            {"name": "published_date", "type": "Text", "enable_search": False},
            {"name": "published_year", "type": "Text", "enable_search": False},
            {"name": "published_month", "type": "Text", "enable_search": False},
            {"name": "height", "type": "Text", "enable_search": False},
            {"name": "width", "type": "Text", "enable_search": False},
            {"name": "thickness", "type": "Text", "enable_search": False},
            {"name": "weight", "type": "Text", "enable_search": False}
        ]
        try:
            InventoryCategory.objects.create(name='Book', code='book', company=company, default_unit=unit,
                                             default_tax_scheme=tax,
                                             track_inventory=True, can_be_sold=True, can_be_purchased=True,
                                             extra_fields=extra_fields)
            messages.success(request, 'Book category created!')
        except IntegrityError:
            messages.error(request, 'Book category already exists!')


create_book_category.short_description = "Create Book Category"


def import_sold_books(modeladmin, request, queryset):
    for company in queryset:
        url = 'https://thuprai.com/book/bestsellers.json'
        sold_list = requests.get(url).json()
        category = InventoryCategory.objects.get(name='Book', code='book', company=company)
        for obj in sold_list:
            item, __ = Item.objects.get_or_create(code=obj[1], company=company,
                                                  defaults={'name': obj[0], 'selling_price': obj[2],
                                                            'unit_id': category.default_unit_id,
                                                            'tax_scheme_id': category.default_tax_scheme_id,
                                                            'category': category})
            if not item.brand_id and obj[3]:
                brand, __ = Brand.objects.get_or_create(name=obj[3], company=company)
                item.brand = brand
                item.save()

        messages.success(request, '{} books imported!'.format(len(sold_list)))


import_sold_books.short_description = "Import Sold Books"


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')
    list_filter = ('organization_type',)
    actions = [create_company_defaults, setup_nepali_tax_schemes, setup_basic_units, create_book_category,
               import_sold_books]

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Company, CompanyAdmin)


class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')

    def start_date(self, obj):
        return obj.start.strftime('%d-%m-%Y')

    def end_date(self, obj):
        return obj.end.strftime('%d-%m-%Y')


admin.site.register(FiscalYear, FiscalYearAdmin)


class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'enabled')
    list_filter = ('user', 'user__company', 'enabled')
    readonly_fields = ('created_at',)
    search_fields = ('user__full_name', 'user__company__name', 'key')
    
admin.site.register(AccessKey, AccessKeyAdmin)
