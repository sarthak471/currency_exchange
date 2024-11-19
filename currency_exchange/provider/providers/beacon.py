import requests
from datetime import datetime
from .base import ExchangeRateProvider

from currency_exchange.settings import BASE_URL , API_KEY


class CurrencyBeaconProvider(ExchangeRateProvider):
    BASE_URL = BASE_URL
    API_KEY = API_KEY

    def fetch_historical_rates(self, source_currency, exchanged_currency, start_date, end_date):
        """Fetch historical rates for a date range."""
        start_date_str = datetime.strptime(str(start_date), "%Y-%m-%d").strftime("%Y-%m-%d")
        end_date_str = datetime.strptime(str(end_date), "%Y-%m-%d").strftime("%Y-%m-%d")
        endpoint = f"{self.BASE_URL}/timeseries"
        params = {
            "api_key": self.API_KEY,
            "base": source_currency,
            "symbols": exchanged_currency if exchanged_currency else "",
            "start_date": start_date_str,
            "end_date": end_date_str,
        }
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise ValueError(f"CurrencyBeacon API error: {response.status_code}")
        data = response.json()
        rates_data = data.get("response", {})
        return rates_data

    def fetch_exchange_rate(self, source_currency, exchanged_currency):
        """
        Fetch the exchange rate and convert a specific amount.
        """
        # Fetch latest rate
        endpoint = f"{self.BASE_URL}/latest"
        params = {
            "api_key": self.API_KEY,
            "base": source_currency,
            "symbols": exchanged_currency,
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if "rates" not in data or exchanged_currency not in data["rates"]:
                raise ValueError(f"Exchange rate for {source_currency} to {exchanged_currency} not found.")

            exchange_rate = data["rates"][exchanged_currency]

            return exchange_rate

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching exchange rate: {e}")
        except ValueError as e:
            raise e