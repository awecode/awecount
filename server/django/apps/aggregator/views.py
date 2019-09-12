from django.core.exceptions import PermissionDenied
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .export import get_zipped_csvs, import_zipped_csvs
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
