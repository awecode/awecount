from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from .export import get_zipped_csvs
from datetime import datetime

def export_data(request):
    if not request.user.is_authenticated or not request.company_id:
        raise PermissionDenied
    #TODO Verify password as well
    zipped_data = get_zipped_csvs(request.company_id)
    response = FileResponse(zipped_data)
    filename = 'accounting_export_{}.zip'.format(datetime.today().date())
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response

