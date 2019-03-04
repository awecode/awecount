from django.db import connection


def get_next_voucher_no(cls, company_id, attr='voucher_no'):
    from django.db.models import Max

    qs = cls.objects.all()
    if company_id:
        qs = qs.filter(company_id=company_id)
    max_voucher_no = qs.aggregate(Max(attr))[attr + '__max']
    if max_voucher_no:
        return int(max_voucher_no) + 1
    else:
        return 1


def zero_for_none(obj):
    if obj is None or obj is '':
        return 0
    else:
        return obj


def none_for_zero(obj):
    if not obj:
        return None
    else:
        return obj


def model_exists_in_db(model):
    return model._meta.db_table in connection.introspection.table_names()


def delete_rows(rows, model):
    if rows:
        for row in rows:
            if row.get('id'):
                instance = model.objects.get(id=row.get('id'))
                instance.delete()
