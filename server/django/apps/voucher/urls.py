from django.urls import path

from . import views

urlpatterns = [
    path("upload-file/", views.FileUploadView.as_view(), name="upload-file"),
    path("v1/invoice-setting-update/", views.InvoiceSettingUpdateView.as_view()),
]
