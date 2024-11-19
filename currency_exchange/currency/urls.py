from django.urls import path
from .views import HealthCheckView , CurrencyRatesListView , CurrencyListCreateView , CurrencyDetailView , ConvertAmountView
from .template_view import BackOfficeDashboardView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path("currencies", CurrencyListCreateView.as_view(), name="currency-list-create"),
    path("currencies/detail", CurrencyDetailView.as_view(), name="currency-detail"),
    path("currency-rates/", CurrencyRatesListView.as_view(), name="currency-rates"),
    path("convert-amount/", ConvertAmountView.as_view(), name="convert-amount"),
    path('backoffice-dashboard/', BackOfficeDashboardView.as_view(), name='backoffice_dashboard'),
]