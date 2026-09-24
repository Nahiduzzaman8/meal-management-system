from django.urls import path

from apps.reports.views import BalanceHistoryReportView, MembersReportView, MonthlyReportView

urlpatterns = [
    path("monthly/", MonthlyReportView.as_view(), name="report-monthly"),
    path("members/", MembersReportView.as_view(), name="report-members"),
    path("balances/", BalanceHistoryReportView.as_view(), name="report-balances"),
]
