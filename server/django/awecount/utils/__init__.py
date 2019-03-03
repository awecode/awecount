from django.db import connection


def get_next_voucher_no(cls, attr):
    from django.db.models import Max

    max_voucher_no = cls.objects.all().aggregate(Max(attr))[attr + '__max']
    if max_voucher_no:
        return max_voucher_no + 1
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
