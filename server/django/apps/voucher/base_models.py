from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.ledger.models import JournalEntry
from apps.product.models import JournalEntry as InventoryJournalEntry
from awecount.utils import wGenerator


class InvoiceModel(models.Model):
    def __str__(self):
        return str(self.voucher_no)

    @property
    def voucher_type(self):
        return self.__class__.__name__

    def is_issued(self):
        return self.status != 'Draft'

    @property
    def amount_in_words(self):
        return wGenerator.convertNumberToWords(self.get_voucher_meta()['grand_total'])

    def get_total_after_row_discounts(self):
        total = 0
        for row in self.rows.filter():
            total += row.total_after_row_discount
        return total

    def get_discount(self, sub_total_after_row_discounts=None):
        """
        :type sub_total_after_row_discounts: float
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total_after_row_discounts = sub_total_after_row_discounts or self.get_total_after_row_discounts()
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total_after_row_discounts * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total_after_row_discounts * (self.discount / 100), False
        return 0, False

    # Used by get_voucher_meta
    def get_voucher_discount_data(self):
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            return {'type': discount_obj.type, 'value': discount_obj.value}
        else:
            return {'type': self.discount_type, 'value': self.discount}

    def get_voucher_meta(self):
        dct = {
            'sub_total': 0,
            'sub_total_after_row_discounts': 0,
            'discount': 0,
            'non_taxable': 0,
            'taxable': 0,
            'tax': 0
        }
        rows_data = []
        # bypass prefetch cache using filter
        for row in self.rows.filter():
            row_data = dict(quantity=row.quantity, rate=row.rate, total=row.rate * row.quantity,
                            row_discount=row.get_discount()[0] if row.has_discount() else 0)
            row_data['gross_total'] = row_data['total'] - row_data['row_discount']
            row_data['tax_rate'] = row.tax_scheme.rate if row.tax_scheme else 0
            dct['sub_total_after_row_discounts'] += row_data['gross_total']
            dct['sub_total'] += row_data['total']
            rows_data.append(row_data)

        voucher_discount_data = self.get_voucher_discount_data()

        for row_data in rows_data:
            if voucher_discount_data['type'] == 'Percent':
                dividend_discount = row_data['gross_total'] * voucher_discount_data['value'] / 100
            elif voucher_discount_data['type'] == 'Amount':
                dividend_discount = row_data['gross_total'] * voucher_discount_data['value'] / dct[
                    'sub_total_after_row_discounts']
            else:
                dividend_discount = 0
            row_data['dividend_discount'] = dividend_discount
            row_data['pure_total'] = row_data['gross_total'] - dividend_discount
            row_data['tax_amount'] = row_data['tax_rate'] * row_data['pure_total'] / 100

            dct['discount'] += row_data['row_discount'] + row_data['dividend_discount']
            dct['tax'] += row_data['tax_amount']

            if row_data['tax_amount']:
                dct['taxable'] += row_data['pure_total']
            else:
                dct['non_taxable'] += row_data['pure_total']

        dct['grand_total'] = dct['sub_total'] - dct['discount'] + dct['tax']

        for key, val in dct.items():
            dct[key] = round(val, 2)

        return dct

    def cancel(self):
        self.status = 'Cancelled'
        self.save()
        self.apply_cancel_transaction()

    def apply_cancel_transaction(self):
        content_type = ContentType.objects.get(model=self.__class__.__name__.lower() + 'row')
        row_ids = self.rows.values_list('id', flat=True)
        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        InventoryJournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        
    def mark_as_resolved(self, status='Resolved'):
        if self.mode == 'Credit' and self.status == 'Issued':
            self.status = status
            self.save()
        else:
            raise ValueError('This voucher cannot be mark as resolved!')

    

    class Meta:
        abstract = True


class InvoiceRowModel(models.Model):
    def __str__(self):
        return str(self.voucher.voucher_no)

    def get_voucher_no(self):
        return self.voucher.voucher_no

    def get_source_id(self):
        return self.voucher_id

    def has_discount(self):
        return True if self.discount_obj_id or self.discount_type in ['Amount', 'Percent'] and self.discount else False

    def get_discount(self):
        """
        returns:
        discount_amount:float, is_trade_discount:boolean
        """
        sub_total = self.quantity * self.rate
        if self.discount_obj_id:
            discount_obj = self.discount_obj
            if discount_obj.type == 'Amount':
                return discount_obj.value, discount_obj.trade_discount
            elif discount_obj.type == 'Percent':
                return sub_total * (discount_obj.value / 100), discount_obj.trade_discount
        elif self.discount and self.discount_type == 'Amount':
            return self.discount, False
        elif self.discount and self.discount_type == 'Percent':
            return sub_total * (self.discount / 100), False
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
