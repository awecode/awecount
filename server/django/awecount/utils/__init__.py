def get_next_voucher_no(cls, attr):
    from django.db.models import Max

    max_voucher_no = cls.objects.all().aggregate(Max(attr))[attr + '__max']
    if max_voucher_no:
        return max_voucher_no + 1
    else:
        return 1
