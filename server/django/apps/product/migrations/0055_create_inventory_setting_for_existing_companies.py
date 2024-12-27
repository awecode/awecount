# your_app_name/migrations/00xx_migration_name.py

from django.db import migrations


def create_inventory_setting(apps, schema_editor):
    # Get the models for the source and destination tables
    InventorySetting = apps.get_model("product", "InventorySetting")
    Company = apps.get_model("users", "Company")

    # Copy data from the source table to the destination table
    for company in Company.objects.all():
        if not InventorySetting.objects.filter(company=company).exists():
            InventorySetting.objects.create(company=company)

class Migration(migrations.Migration):
    dependencies = [
        ("product", "0054_inventorysetting"),
    ]

    operations = [
        # Add any other operations you need before the data copy
        migrations.RunPython(create_inventory_setting),
    ]