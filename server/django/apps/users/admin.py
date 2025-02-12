import requests
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.admin import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.admin import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.company.models import Company, CompanyMember, FiscalYear, Permission
from apps.ledger.models import handle_company_creation
from apps.product.helpers import create_book_category
from apps.product.models import Brand, Item, Unit
from apps.product.models import Category as InventoryCategory
from apps.tax.models import TaxScheme
from apps.voucher.models.voucher_settings import (
    handle_company_creation as create_settings,
)

from .models import Role, User

admin.site.unregister(Group)

admin.site.site_header = "Awecount"
admin.site.site_title = "Awecount Admin Portal"
admin.site.index_title = "Welcome to Awecount"


def create_company_defaults(modeladmin, request, queryset):
    for company in queryset:
        handle_company_creation(modeladmin, company=company)
        create_settings(modeladmin, company=company)


create_company_defaults.short_description = "Create company defaults"


class UserCreationForm(DjangoUserCreationForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

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


class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    form = UserChangeForm
    add_form = UserCreationForm
    filter_horizontal = ()
    list_display_links = (
        "id",
        "full_name",
        "email",
        "date_joined",
    )
    list_display = (
        "id",
        "full_name",
        "email",
        "date_joined",
        "company",
        "is_superuser",
    )
    list_filter = ("is_superuser",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name",
                    "email",
                    "password",
                    "date_joined",
                    "last_login",
                    "is_superuser",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name",
                    "email",
                    "password1",
                    "password2",
                    "company",
                )
            },
        ),
    )
    search_fields = (
        "full_name",
        "email",
        "company__name",
        "is_superuser",
    )
    readonly_fields = (
        "is_superuser",
        "date_joined",
        "last_login",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Role)


def setup_nepali_tax_schemes(modeladmin, request, queryset):
    for company in queryset:
        try:
            tax_schemes = TaxScheme.setup_nepali_tax_schemes(company)
            messages.success(
                request, "{} tax scheme(s) created!".format(len(tax_schemes))
            )
        except IntegrityError:
            messages.error(request, "One or more tax schemes already exist!")


setup_nepali_tax_schemes.short_description = "Setup Nepali Tax Schemes"


def setup_basic_units(modeladmin, request, queryset):
    for company in queryset:
        try:
            units = Unit.create_default_units(company)
            messages.success(request, "{} unit(s) created!".format(len(units)))
        except IntegrityError:
            messages.error(request, "One or more units already exist!")


setup_basic_units.short_description = "Setup Basic Units"


def create_book_category_for_companies(modeladmin, request, queryset):
    for company in queryset:
        try:
            create_book_category(company)
            messages.success(request, "Book category created!")
        except ValidationError:
            messages.error(request, "Book category already exists!")


create_book_category_for_companies.short_description = "Create Book Category"


def import_sold_books(modeladmin, request, queryset):
    for company in queryset:
        url = "https://thuprai.com/book/bestsellers.json"
        sold_list = requests.get(url).json()
        category = InventoryCategory.objects.get(
            name="Book", code="book", company=company
        )
        for obj in sold_list:
            item, __ = Item.objects.get_or_create(
                code=obj[1],
                company=company,
                defaults={
                    "name": obj[0],
                    "selling_price": obj[2],
                    "unit_id": category.default_unit_id,
                    "tax_scheme_id": category.default_tax_scheme_id,
                    "category": category,
                },
            )
            if not item.brand_id and obj[3]:
                brand, __ = Brand.objects.get_or_create(name=obj[3], company=company)
                item.brand = brand
                item.save()

        messages.success(request, "{} books imported!".format(len(sold_list)))


import_sold_books.short_description = "Import Sold Books"


class CompanyAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "address",
        "phone",
        "email",
        "alternate_email",
        "tax_registration_number",
    )
    list_display = (
        "name",
        "address",
        "phone",
        "email",
        "tax_registration_number",
    )
    list_filter = ("organization_type",)
    actions = [
        create_company_defaults,
        setup_nepali_tax_schemes,
        setup_basic_units,
        create_book_category_for_companies,
        import_sold_books,
    ]

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Company, CompanyAdmin)


class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")

    def start_date(self, obj):
        return obj.start_date.strftime("%d-%m-%Y")

    def end_date(self, obj):
        return obj.end_date.strftime("%d-%m-%Y")


admin.site.register(FiscalYear, FiscalYearAdmin)


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ("company", "member", "access_level")
    search_fields = ("company__name", "member__full_name")
    list_filter = ("access_level",)
    actions = [create_company_defaults]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
