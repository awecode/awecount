import json
from datetime import datetime

import tablib
from auditlog.models import LogEntry
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import FileResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.users.models import AccessKey
from apps.voucher.models import SalesVoucher
from .export import get_zipped_csvs, import_zipped_csvs
from .resources import LogEntryResource


@csrf_exempt
def export_data(request):
    data = json.loads(request.body)
    user = authenticate(email=data.get('email'), password=data.get('password'))
    if user and request.user == user:
        zipped_data = get_zipped_csvs(request.company_id)
        response = FileResponse(zipped_data)
        filename = 'accounting_export_{}.zip'.format(datetime.today().date())
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response
    else:
        return JsonResponse({'detail': 'Please provide valid credential!'}, status=401)


@csrf_exempt
def import_data(request):
    data = request.POST
    user = authenticate(email=data.get('email'), password=data.get('password'))

    if user and request.user == user:
        result = import_zipped_csvs(request.company_id, request.FILES.get('file'))
        return JsonResponse(result)

    else:
        return JsonResponse({'detail': 'Please provide valid credential!'}, status=401)


# not a real view
def qs_to_xls(querysets):
    datasets = []
    for title, qs, Resource in querysets:
        # resource = resources.modelresource_factory(model=qs.model, resource_class=FilteredResource)()
        resource = Resource()
        data = resource.export(queryset=qs)
        data.title = title
        datasets.append(data)
    book = tablib.Databook(datasets)
    xls = book.xls
    response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = '{}_{}.xls'.format(qs.model.__name__ + '_', datetime.today().date())
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


@csrf_exempt
def export_auditlog(request):
    if not request.user.is_authenticated or not request.company_id:
        raise PermissionDenied
    resource = LogEntryResource()
    qs = LogEntry.objects.filter(actor__company_id=request.user.company_id).select_related('content_type', 'actor')
    dataset = resource.export(queryset=qs)
    dataset.title = 'Audit Logs'
    xls = dataset.xls
    response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = '{}_{}.xls'.format('Log_Entries_', datetime.today().date())
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


@csrf_exempt
def sales_invoice_api(request):
    if request.method != 'POST':
        raise PermissionDenied
    data = request.POST
    required_fields = ['status', 'mode']
    for field in required_fields:
        if field not in data:
            raise SuspiciousOperation('{} field is required!'.format(field))
    user = AccessKey.get_user(request.META.get('HTTP_SECRET'))
    company = user.company
    voucher = SalesVoucher(
        customer_name = data.get('customer_name'),
        address=data.get('address'),
        date=datetime.today(),
        status = data.get('status'),
        discount = data.get('discount') or 0,
        discount_type=data.get('discount_type'),
        trade_discount=data.get('trade_discount') or False,
        mode=data.get('mode'),
        remarks=data.get('remarks'),
        user=user,
        company=company,
        fiscal_year_id=company.current_fiscal_year_id
    )
    #voucher_no
    voucher.save()
    return JsonResponse({})