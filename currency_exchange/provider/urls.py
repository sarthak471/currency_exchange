from django.urls import path
from .views import HealthCheckView , ProviderView , ProviderPriorityUpdateView , HistoricalDataLoaderView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('list', ProviderView.as_view(), name='provider-list'),
    path('update-priority', ProviderPriorityUpdateView.as_view(), name='provider-update-priority'),
    path('load-historical-data', HistoricalDataLoaderView.as_view(), name="load_historical_data"),
]
