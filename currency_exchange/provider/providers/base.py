from abc import ABC, abstractmethod

class ExchangeRateProvider(ABC):
    @abstractmethod
    def fetch_historical_rates(self, source_currency, exchanged_currency, start_date, end_date):
        """Fetch historical exchange rates for a date range."""
        pass

    @abstractmethod
    def fetch_exchange_rate(self, source_currency, exchanged_currency):
        """Fetch exchange rate for a specific date or the latest rate."""
        pass