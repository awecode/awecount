import tablib
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from import_export import resources

from .export import get_zipped_csvs, import_zipped_csvs, FilteredResource
from datetime import datetime


@csrf_exempt
def export_data(request):
    if not request.user.is_authenticated or not request.company_id:
        raise PermissionDenied
    # TODO Verify password as well
    zipped_data = get_zipped_csvs(request.company_id)
    response = FileResponse(zipped_data)
    filename = 'accounting_export_{}.zip'.format(datetime.today().date())
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


@csrf_exempt
def import_data(request):
    if not request.user.is_authenticated or not request.company_id:
        raise PermissionDenied
    # TODO Verify password as well
    result = import_zipped_csvs(request.company_id, request.FILES.get('import_file'))
    return JsonResponse(result)

#not a real view
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
    # import ipdb
    # ipdb.set_trace()
    # response = FileResponse(xls)
    response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = '{}_{}.xls'.format(qs.model.__name__, datetime.today().date())
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response