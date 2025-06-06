# Generated by Django 4.2.20 on 2025-05-06 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0005_alter_account_current_cr_alter_account_current_dr_and_more'),
        ('tax', '0003_alter_taxscheme_short_name'),
        ('voucher', '0011_alter_landedcostrow_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='landedcostrow',
            name='credit_account',
            field=models.ForeignKey(help_text='Account to which the landed cost will be credited', on_delete=django.db.models.deletion.CASCADE, related_name='landed_cost_rows', to='ledger.account'),
        ),
        migrations.AddField(
            model_name='landedcostrow',
            name='tax_scheme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='landed_cost_rows', to='tax.taxscheme'),
        ),
    ]
