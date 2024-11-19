from faker import Faker
from datetime import datetime, timedelta
from provider.providers.base import ExchangeRateProvider

class MockProvider(ExchangeRateProvider):
    def __init__(self):
        self.fake = Faker()

    def generate_fake_exchange_rate(self, source_currency, exchanged_currency):
        """Generate a fake exchange rate between two currencies."""
        return round(self.fake.random_number(digits=3) / 100, 8)

    def generate_fake_historical_rates(self, source_currency, exchanged_currency, start_date, end_date):
        """Generate fake historical exchange rates for a date range with multiple currencies."""

        # Split exchanged_currency string into a list of currencies
        currency_list = exchanged_currency.split(",") if exchanged_currency else []

        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        historical_data = {}

        for date in date_list:
            daily_rates = {}
            for currency in currency_list:
                daily_rates[currency] = self.generate_fake_exchange_rate(source_currency, currency)
            historical_data[date] = daily_rates
        return historical_data

    async def fetch_historical_rates(self, source_currency, exchanged_currency, start_date, end_date):
        """Fetch fake historical rates for a date range."""
        rates_data = self.generate_fake_historical_rates(source_currency, exchanged_currency, start_date, end_date)
        return rates_data

    def fetch_exchange_rate(self, source_currency, exchanged_currency):
        """Fetch a fake exchange rate for a pair of currencies."""
        exchange_rate = self.generate_fake_exchange_rate(source_currency, exchanged_currency)
        return exchange_rate
