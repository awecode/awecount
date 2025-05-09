# Generated by Django 4.2.17 on 2025-01-15 06:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
        ('ledger', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillOfMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('quantity', models.FloatField()),
                ('rate', models.FloatField()),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BillOfMaterialRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('quantity', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('hs_code', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000)])),
                ('items_sales_account_type', models.CharField(blank=True, choices=[('dedicated', 'Use dedicated account'), ('global', 'Use global account'), ('existing', 'Use existing account'), ('category', 'Use category specific account'), ('creation', 'Choose during item creation')], max_length=100, null=True)),
                ('items_purchase_account_type', models.CharField(blank=True, choices=[('dedicated', 'Use dedicated account'), ('global', 'Use global account'), ('existing', 'Use existing account'), ('category', 'Use category specific account'), ('creation', 'Choose during item creation')], max_length=100, null=True)),
                ('items_discount_allowed_account_type', models.CharField(blank=True, choices=[('dedicated', 'Use dedicated account'), ('global', 'Use global account'), ('existing', 'Use existing account'), ('category', 'Use category specific account'), ('creation', 'Choose during item creation')], max_length=100, null=True)),
                ('items_discount_received_account_type', models.CharField(blank=True, choices=[('dedicated', 'Use dedicated account'), ('global', 'Use global account'), ('existing', 'Use existing account'), ('category', 'Use category specific account'), ('creation', 'Choose during item creation')], max_length=100, null=True)),
                ('track_inventory', models.BooleanField(default=True)),
                ('can_be_sold', models.BooleanField(default=True)),
                ('can_be_purchased', models.BooleanField(default=True)),
                ('fixed_asset', models.BooleanField(default=False)),
                ('direct_expense', models.BooleanField(default=False)),
                ('indirect_expense', models.BooleanField(default=False)),
                ('extra_fields', models.JSONField(blank=True, default=list, null=True)),
                ('use_account_subcategory', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='InventoryAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('name', models.CharField(max_length=255)),
                ('account_no', models.PositiveIntegerField(blank=True, null=True)),
                ('current_balance', models.FloatField(default=0)),
                ('opening_balance', models.FloatField(default=0)),
                ('opening_balance_rate', models.FloatField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='InventoryAdjustmentVoucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_sub_total', models.FloatField(blank=True, null=True)),
                ('meta_sub_total_after_row_discounts', models.FloatField(blank=True, null=True)),
                ('meta_discount', models.FloatField(blank=True, null=True)),
                ('meta_non_taxable', models.FloatField(blank=True, null=True)),
                ('meta_taxable', models.FloatField(blank=True, null=True)),
                ('meta_tax', models.FloatField(blank=True, null=True)),
                ('voucher_no', models.PositiveIntegerField(blank=True, null=True)),
                ('date', models.DateField()),
                ('issue_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('Issued', 'Issued'), ('Cancelled', 'Cancelled')], max_length=225)),
                ('purpose', models.CharField(choices=[('Stock In', 'Stock In'), ('Stock Out', 'Stock Out'), ('Damaged', 'Damaged'), ('Expired', 'Expired')], max_length=225)),
                ('remarks', models.TextField()),
                ('total_amount', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryAdjustmentVoucherRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('rate', models.FloatField()),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('amount', models.FloatField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryConversionVoucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('meta_sub_total', models.FloatField(blank=True, null=True)),
                ('meta_sub_total_after_row_discounts', models.FloatField(blank=True, null=True)),
                ('meta_discount', models.FloatField(blank=True, null=True)),
                ('meta_non_taxable', models.FloatField(blank=True, null=True)),
                ('meta_taxable', models.FloatField(blank=True, null=True)),
                ('meta_tax', models.FloatField(blank=True, null=True)),
                ('voucher_no', models.PositiveIntegerField(blank=True, null=True)),
                ('date', models.DateField()),
                ('issue_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('Issued', 'Issued'), ('Cancelled', 'Cancelled')], max_length=225)),
                ('remarks', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryConversionVoucherRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('rate', models.FloatField(blank=True, null=True)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('transaction_type', models.CharField(blank=True, choices=[('Cr', 'Cr'), ('Dr', 'Dr')], max_length=16, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventorySetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_fifo', models.BooleanField(default=False)),
                ('enable_negative_stock_check', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('object_id', models.PositiveIntegerField()),
                ('source_voucher_no', models.CharField(blank=True, max_length=50, null=True)),
                ('source_voucher_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_journal_entries', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name_plural': 'Inventory Journal Entries',
            },
        ),
        migrations.CreateModel(
            name='TransatcionRemovalLog',
            fields=[
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
                ('row_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('Ledger', 'Ledger'), ('Inventory', 'Inventory')], max_length=50)),
                ('row_dump', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('short_name', models.CharField(blank=True, max_length=10, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dr_amount', models.FloatField(blank=True, null=True)),
                ('cr_amount', models.FloatField(blank=True, null=True)),
                ('current_balance', models.FloatField(blank=True, null=True)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('remaining_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('consumption_data', models.JSONField(blank=True, default=dict)),
                ('fifo_inconsistency_quantity', models.FloatField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='product.inventoryaccount')),
                ('journal_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='product.journalentry')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('voucher_no', models.PositiveBigIntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('selling_price', models.FloatField(blank=True, null=True)),
                ('cost_price', models.FloatField(blank=True, null=True)),
                ('front_image', models.ImageField(blank=True, null=True, upload_to='item_front_images/')),
                ('back_image', models.ImageField(blank=True, null=True, upload_to='item_back_images/')),
                ('sales_account_type', models.CharField(blank=True, choices=[('global', 'Global'), ('dedicated', 'Dedicated'), ('category', 'Category'), ('existing', 'Existing')], max_length=16, null=True)),
                ('purchase_account_type', models.CharField(blank=True, choices=[('global', 'Global'), ('dedicated', 'Dedicated'), ('category', 'Category'), ('existing', 'Existing')], max_length=16, null=True)),
                ('discount_allowed_account_type', models.CharField(blank=True, choices=[('global', 'Global'), ('dedicated', 'Dedicated'), ('category', 'Category'), ('existing', 'Existing')], max_length=16, null=True)),
                ('discount_received_account_type', models.CharField(blank=True, choices=[('global', 'Global'), ('dedicated', 'Dedicated'), ('category', 'Category'), ('existing', 'Existing')], max_length=16, null=True)),
                ('track_inventory', models.BooleanField(default=True)),
                ('can_be_sold', models.BooleanField(default=True)),
                ('can_be_purchased', models.BooleanField(default=True)),
                ('fixed_asset', models.BooleanField(default=False)),
                ('direct_expense', models.BooleanField(default=False)),
                ('indirect_expense', models.BooleanField(default=False)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('search_data', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item', to='product.inventoryaccount')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='product.brand')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='product.category')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='company.company')),
                ('dedicated_discount_allowed_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discount_allowed_item_dedicated', to='ledger.account')),
                ('dedicated_discount_received_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discount_received_item_dedicated', to='ledger.account')),
                ('dedicated_purchase_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_item_dedicated', to='ledger.account')),
                ('dedicated_sales_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_item_dedicated', to='ledger.account')),
                ('discount_allowed_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discount_allowed_item', to='ledger.account')),
                ('discount_received_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discount_received_item', to='ledger.account')),
                ('expense_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_item', to='ledger.account')),
                ('fixed_asset_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fixed_asset_item', to='ledger.account')),
                ('purchase_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_item', to='ledger.account')),
                ('sales_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_item', to='ledger.account')),
            ],
        ),
    ]
