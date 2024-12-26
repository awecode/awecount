from apps.product.models import Category as InventoryCategory
from apps.product.models import Unit
from apps.tax.models import TaxScheme


def create_book_category(company):
    unit, __ = Unit.objects.get_or_create(
        short_name="pcs", company=company, defaults={"name": "Pieces"}
    )
    tax, __ = TaxScheme.objects.get_or_create(
        short_name="Taxless",
        company=company,
        defaults={"name": "Taxless", "rate": 0},
    )
    extra_fields = [
        {"name": "localized_title", "type": "Text", "enable_search": True},
        {"name": "english_subtitle", "type": "Text", "enable_search": False},
        {"name": "localized_subtitle", "type": "Text", "enable_search": False},
        {"name": "english_description", "type": "Text", "enable_search": False},
        {"name": "localized_description", "type": "Text", "enable_search": False},
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
        {"name": "weight", "type": "Text", "enable_search": False},
    ]
    return InventoryCategory.objects.create(
        name="Book",
        code="book",
        company=company,
        default_unit=unit,
        default_tax_scheme=tax,
        track_inventory=True,
        can_be_sold=True,
        can_be_purchased=True,
        extra_fields=extra_fields,
    )
