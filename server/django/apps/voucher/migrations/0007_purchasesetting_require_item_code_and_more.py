# Generated by Django 4.2.20 on 2025-05-02 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0006_merge_20250501_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasesetting',
            name='require_item_code',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='purchasesetting',
            name='require_item_hs_code',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salessetting',
            name='require_item_code',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salessetting',
            name='require_item_hs_code',
            field=models.BooleanField(default=False),
        ),
    ]
