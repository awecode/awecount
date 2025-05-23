# Generated by Django 4.2.20 on 2025-05-06 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0009_alter_landedcostrow_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasesetting',
            name='enable_landed_cost',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='purchasesetting',
            name='landed_cost_accounts',
            field=models.JSONField(default=dict, blank=True),
        ),
    ]
