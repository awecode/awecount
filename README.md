Find journal voucher with duplicate accounts - this should be prevented
```
JournalVoucher.objects.values('rows__account_id', 'id').annotate(cnt=Count('rows__account_id')).values_list('id', flat=True).filter(cnt__gt=1)
```