import asyncio
from datetime import datetime
from django.db import transaction
from currency.models import Currency , CurrencyExchangeRate
from provider.providers.provider_factory import ProviderFactory


async def fetch_and_store_rates(provider_name, source_currency, target_currencies, start_date, end_date):
    """
    Fetch historical rates from a provider and store them in the database.
    """
    # Convert start_date and end_date to datetime.date objects if they are strings
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    provider = ProviderFactory.get_provider_adapter(provider_name=provider_name)
    try:
        fetched_rates = provider.fetch_historical_rates(
            source_currency,
            ",".join(target_currencies),
            start_date,
            end_date,
        )
        # Save the data asynchronously
        await save_rates_to_db(source_currency, fetched_rates)
    except Exception as e:
        print(f"Error fetching rates from provider {provider_name}: {e}")


async def save_rates_to_db(source_currency, fetched_rates):
    """
    Save fetched rates to the database.
    """
    try:
        with transaction.atomic():
            for rate in fetched_rates:
                CurrencyExchangeRate.objects.update_or_create(
                    source_currency=Currency.objects.get(code=source_currency),
                    exchanged_currency=Currency.objects.get(code=rate["currency"]),
                    valuation_date=rate["date"],
                    defaults={"rate_value": rate["rate"]},
                )
    except Exception as e:
        print(f"Error saving rates to the database: {e}")


async def load_historical_data(provider_name, source_currency, exchanged_currencies, start_date, end_date):
    """
    Load historical data for the given parameters.
    """
    tasks = []
    batch_size = 5  # Batch size to limit API calls per request
    for i in range(0, len(exchanged_currencies), batch_size):
        batch = exchanged_currencies[i:i + batch_size]
        tasks.append(fetch_and_store_rates(provider_name, source_currency, batch, start_date, end_date))

    await asyncio.gather(*tasks)