from import_export.fields import Field
from import_export.resources import Resource


class AgeingReportResource(Resource):
    total_30 = Field(attribute="total_30", column_name="30 days")

    # class Meta:
    #     fields = ["total_30"]
