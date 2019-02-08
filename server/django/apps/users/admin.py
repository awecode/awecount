from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Company

admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'email', 'company__name')
    list_filter = ('company', 'is_superuser')
    list_display = ('full_name', 'email', 'company')
    exclude = ('password',)
    readonly_fields = ('last_login', 'date_joined', 'is_superuser')


admin.site.register(User, UserAdmin)


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')
    list_display = ('name', 'address', 'contact_no', 'email', 'tax_registration_number')
    list_filter = ('organization_type',)


admin.site.register(Company, CompanyAdmin)
