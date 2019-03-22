from django.urls import path

from . import views

urlpatterns = [
    path('pdf/sale-voucher/<int:pk>', views.SalesVoucherPdfView.as_view()),
]
