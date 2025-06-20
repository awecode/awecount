import random
from copy import deepcopy

from django.db import transaction
from django.conf import settings
from awecount.libs.helpers import (
    add_time_to_date,
    deserialize_request,
)
from django.core.mail import EmailMessage
from apps.voucher.models import RecurringVoucherTemplate

@transaction.atomic
def generate_voucher(template_id):
    template = RecurringVoucherTemplate.objects.get(id=template_id)
    invoice_data = deepcopy(template.invoice_data)

    request = deserialize_request(
        {
            "user": template.user,
            "company": template.company,
            "company_id": template.company.id,
            "user_id": template.user.id,
            "data": invoice_data,
        }
    )
    if template.type == "Sales Voucher":
        from apps.voucher.serializers.sales import SalesVoucherCreateSerializer

        invoice_data["date"] = template.next_date
        invoice_data["due_date"] = add_time_to_date(
            template.next_date, template.due_date_after, template.due_date_after_time_unit
        )
        invoice_data["status"] = "Issued"
        serializer = SalesVoucherCreateSerializer(
            data=invoice_data,
            context={
                "request": request,
            },
        )
        serializer.is_valid(raise_exception=True)
        voucher = serializer.save()
    else:
        from apps.voucher.serializers.purchase import (
            PurchaseVoucherCreateSerializer,
        )

        invoice_data["date"] = template.next_date
        invoice_data["due_date"] = add_time_to_date(
            template.next_date, template.due_date_after, template.due_date_after_time_unit
        )
        invoice_data["status"] = "Issued"
        invoice_data["voucher_no"] = "auto-{}-{}-{}".format(
            template.id, template.no_of_vouchers_created + 1, random.randint(1000, 9999)
        )
        voucher = PurchaseVoucherCreateSerializer(
            data=invoice_data,
            context={
                "request": request,
            },
        )
        voucher.is_valid(raise_exception=True)
        voucher = voucher.save()

    if template.send_email:
        success_message = f"""
        <html>
            <body>
                <h1>Recurring {template.type} Generated Successfully</h1>
                <p>Dear {template.user.full_name},</p>
                <p>We are pleased to inform you that the recurring {template.type.lower()} titled <strong>{template.title}</strong> has been successfully generated.</p>
            <p>You can view the generated voucher in the dashboard. If you encounter any issues, please contact us.</p>
            </body>
        </html>
        """

        email = EmailMessage(
            subject="Recurring Voucher Generated Successfully",
            body=success_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[template.user.email],
        )
        email.content_subtype = "html"
        email.send()

    template.no_of_vouchers_created += 1
    template.last_generated = template.next_date
    template.save()