import json
from datetime import datetime

import tablib
from auditlog.models import LogEntry
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .export import get_zipped_csvs, import_zipped_csvs
from .resources import LogEntryResource


@csrf_exempt
def export_data(request):
    data = json.loads(request.body)
    user = authenticate(email=data.get("email"), password=data.get("password"))
    if user and request.user == user:
        zipped_data = get_zipped_csvs(request.company.id)
        response = FileResponse(zipped_data)
        filename = "accounting_export_{}.zip".format(datetime.today().date())
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response
    else:
        return JsonResponse({"detail": "Please provide valitd credential!"}, status=401)


@csrf_exempt
def import_data(request):
    data = request.POST
    user = authenticate(email=data.get("email"), password=data.get("password"))

    if user and request.user == user:
        # TODO Move as background job
        result = import_zipped_csvs(request.company.id, request.FILES.get("file"))
        return JsonResponse(result)
    else:
        return JsonResponse({"detail": "Please provide valid credential!"}, status=401)


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
    for sheet in book.sheets():
        column_sums = [0] * len(sheet.headers)
        for row in sheet:
            for idx, header in enumerate(sheet.headers):
                value = row[idx]
                if isinstance(value, (int, float)):
                    column_sums[idx] += value
        csum = []
        for x in column_sums:
            csum.append("") if not x else csum.append(round(x, 2))
        csum[0] = "Total"
        sheet.append(csum)
    xls = book.xls
    response = HttpResponse(
        xls,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    filename = "{}_{}.xls".format(qs.model.__name__ + "_", datetime.today().date())
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    return response


@csrf_exempt
def export_auditlog(request):
    if not request.user.is_authenticated or not request.company.id:
        raise PermissionDenied
    resource = LogEntryResource()
    qs = LogEntry.objects.filter(
        actor__company_id=request.company.id
    ).select_related("content_type", "actor")
    dataset = resource.export(queryset=qs)
    dataset.title = "Audit Logs"
    xls = dataset.xls
    response = HttpResponse(
        xls,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    filename = "{}_{}.xls".format("Log_Entries_", datetime.today().date())
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    return response
