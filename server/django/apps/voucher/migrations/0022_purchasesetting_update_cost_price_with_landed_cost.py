# Generated by Django 4.2.20 on 2025-06-02 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0021_merge_20250602_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasesetting',
            name='update_cost_price_with_landed_cost',
            field=models.BooleanField(default=False),
        ),
    ]
