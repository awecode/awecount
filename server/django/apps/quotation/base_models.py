from django.db import models

class QuotationRowModel(models.Model):
    company_id_accessor = "voucher__company_id"

    def __str__(self):
        return str(self.voucher.voucher_no)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher_id

    def has_discount(self):
        return (
            True
            if self.discount_obj_id
            or self.discount_type in ["Amount", "Percent"]
            and self.discount
            else False
        )

    def get_discount(self):
        """
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total = self.quantity * self.rate
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == "Amount":
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == "Percent":
                return sub_total * (
                    discount_obj.value / 100
                ), discount_obj.trade_discount
        elif self.discount and self.discount_type == "Amount":
            return self.discount, self.trade_discount
        elif self.discount and self.discount_type == "Percent":
            return sub_total * (self.discount / 100), self.trade_discount
        return 0, False

    def get_tax_amount(self):
        amount = 0
        if self.tax_scheme:
            amount = (self.tax_scheme.rate / 100) * self.total
        return amount

    @property
    def total(self):
        row_total = self.quantity * self.rate
        # sub_total = sub_total - self.get_discount()[0]
        return row_total

    @property
    def total_after_row_discount(self):
        row_total = self.quantity * self.rate
        row_total = row_total - self.get_discount()[0]
        return row_total

    class Meta:
        abstract = True
