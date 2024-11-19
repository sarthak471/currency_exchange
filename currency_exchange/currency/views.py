import logging
from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CurrencyRatesListRequestSerializer,
    ConvertAmountRequestSerializer,
)

from provider.providers.provider_factory import ProviderFactory

from currency.models import Currency
from currency.serializers import CurrencySerializer
from currency.models import Currency, CurrencyExchangeRate

logger = logging.getLogger("django")

class HealthCheckView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/currency/health

    Content-Type: application/json

    Description:
    This API provides a health check to ensure that the application is running correctly.
    It returns a simple response with a 'healthy' status.
    """

    def get(self, request, *args, **kwargs):
        logger.info("Health check request received.")
        data = {
            "status": "healthy",
            "message": "Application is running smoothly.",
        }
        return Response(data, status=status.HTTP_200_OK)


class CurrencyListCreateView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/currency/currencies

    Authorization: token <token> (included in request headers)
    Content-Type: application/json

    Description:
    This API handles two actions:
    - GET: List all available currencies.
    - POST: Create a new currency in the database.

    Returns:
    - GET: A JSON response containing a list of all currencies.
    - POST: A JSON response with the created currency data, or validation errors if the input data is invalid.
    """

    def get(self, request):
        logger.info("Listing all currencies.")
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        logger.info("Creating a new currency.")
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Currency created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Currency creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyDetailView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/currencies/

    Content-Type: application/json

    Description:
    This API handles three actions for a specific currency:
    - GET: Retrieve a currency by its code.
    - PUT: Update an existing currency by its code.
    - DELETE: Delete a currency by its code.

    Returns:
    - GET: A JSON response with the currency details.
    - PUT: A JSON response with the updated currency data, or validation errors.
    - DELETE: A JSON response indicating successful deletion, or an error message if the currency is not found.
    """

    def get_object_by_code(self, code):
        try:
            return Currency.objects.get(code=code)
        except Currency.DoesNotExist:
            return None

    def get(self, request):
        """
        Retrieve a currency by its code.
        """
        currency_code = request.data.get("code")
        if not currency_code:
            logger.warning("Currency code is required for GET request.")
            return Response(
                {"error": "Currency code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        currency = self.get_object_by_code(currency_code)
        if not currency:
            logger.warning(f"Currency with code {currency_code} not found.")
            return Response(
                {"error": f"Currency with code {currency_code} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CurrencySerializer(currency)
        logger.info(f"Currency retrieved: {currency_code}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update a currency by its code.
        """
        currency_code = request.data.get("code")
        if not currency_code:
            logger.warning("Currency code is required for PUT request.")
            return Response(
                {"error": "Currency code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        currency = self.get_object_by_code(currency_code)
        if not currency:
            logger.warning(f"Currency with code {currency_code} not found.")
            return Response(
                {"error": f"Currency with code {currency_code} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CurrencySerializer(currency, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Currency with code {currency_code} updated successfully.")
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Failed to update currency with code {currency_code}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Delete a currency by its code.
        """
        currency_code = request.data.get("code")
        if not currency_code:
            logger.warning("Currency code is required for DELETE request.")
            return Response(
                {"error": "Currency code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        currency = self.get_object_by_code(currency_code)
        if not currency:
            logger.warning(f"Currency with code {currency_code} not found.")
            return Response(
                {"error": f"Currency with code {currency_code} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        currency.delete()
        logger.info(f"Currency with code {currency_code} deleted successfully.")
        return Response(
            {"message": f"Currency with code {currency_code} deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class CurrencyRatesListView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/currency/rates-list/

    Content-Type: application/json

    Description:
    This API retrieves historical exchange rates for a given source currency against all other available currencies,
    within a specified date range. It first checks the database for exchange rates, and if any rates are missing,
    it fetches the missing rates from the specified provider.

    Query Parameters:
    - source_currency (str): The source currency code (e.g., USD).
    - start_date (str): The start date for the date range (format: YYYY-MM-DD).
    - end_date (str): The end date for the date range (format: YYYY-MM-DD).
    - provider_name (str, optional): The name of the provider to fetch missing rates from (e.g., 'mock').
    """

    def get(self, request):
        # Log the request query parameters
        logger.info(f"Received request for historical currency rates: {request.query_params}")

        # Validate incoming query parameters using the serializer
        serializer = CurrencyRatesListRequestSerializer(data=request.query_params)
        if serializer.is_valid():
            source_currency = serializer.validated_data["source_currency"]
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            provider_name = serializer.validated_data.get("provider_name", None)

            # Get all available currencies excluding the source_currency
            all_currencies = Currency.objects.exclude(code=source_currency)
            logger.info(f"All currencies excluding {source_currency}: {all_currencies}")

            # Query for exchange rates in the database for all currencies
            exchange_rates = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                exchanged_currency__in=all_currencies,
                valuation_date__range=(start_date, end_date),
            ).order_by("valuation_date")
            logger.info(f"Exchange rates from database: {exchange_rates}")

            # Initialize response data
            rates_data = []

            # Fetch from the database if rates are available for all currencies
            if exchange_rates.exists():
                # Ensure that rates exist for every currency in `all_currencies`
                all_currencies_codes = [currency.code for currency in all_currencies]
                for valuation_date in exchange_rates.values_list("valuation_date", flat=True).distinct():
                    daily_rates = exchange_rates.filter(valuation_date=valuation_date)

                    # Identify missing exchange rates for currencies not present in the database
                    missing_currencies = [
                        currency.code
                        for currency in all_currencies
                        if currency.code not in daily_rates.values_list('exchanged_currency__code', flat=True)
                    ]
                    logger.info(f"Missing currencies for {valuation_date}: {missing_currencies}")

                    # If there are missing currencies, fetch from the provider
                    if missing_currencies:
                        provider = ProviderFactory.get_provider_adapter(provider_name)
                        try:
                            fetched_rates = provider.fetch_historical_rates(
                                source_currency,
                                ",".join(missing_currencies),  # Only fetch missing currencies
                                start_date,
                                end_date,
                            )
                            logger.info(f"Fetched missing rates from provider: {fetched_rates}")

                            # Save the fetched rates in the database
                            for exchanged_currency, rate_value in fetched_rates.items():
                                try:
                                    exchanged_currency_obj = Currency.objects.get(code=exchanged_currency)
                                    CurrencyExchangeRate.objects.update_or_create(
                                        source_currency=Currency.objects.get(code=source_currency),
                                        exchanged_currency=exchanged_currency_obj,
                                        valuation_date=valuation_date,
                                        defaults={"rate_value": rate_value},
                                    )
                                except Currency.DoesNotExist:
                                    logger.error(f"Currency '{exchanged_currency}' does not exist in the database.")
                                    continue
                        except Exception as e:
                            logger.error(f"Error fetching missing rates from provider: {str(e)}")
                            return Response(
                                {"error": f"Failed to fetch missing rates: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )

                        # Re-query the exchange rates after saving
                        daily_rates = exchange_rates.filter(valuation_date=valuation_date)

                    # Collect rates for each currency for the given valuation_date
                    rates = {
                        rate.exchanged_currency.code: rate.rate_value
                        for rate in daily_rates
                    }
                    rates_data.append({"valuation_date": valuation_date, "rates": rates})

                return Response(rates_data, status=status.HTTP_200_OK)

            # If no data is found in the database, use external provider for all currencies
            logger.info(f"No rates found in database, fetching all rates from provider for {start_date} to {end_date}.")
            provider = ProviderFactory.get_provider_adapter(provider_name)
            all_currencies_codes = [currency.code for currency in all_currencies]
            try:
                fetched_rates = provider.fetch_historical_rates(
                    source_currency,
                    ",".join(all_currencies_codes),  # Fetch all currencies
                    start_date,
                    end_date,
                )
                logger.info(f"Fetched rates from provider: {fetched_rates}")
            except Exception as e:
                logger.error(f"Error fetching rates from provider: {str(e)}")
                return Response(
                    {"error": f"Failed to fetch rates from provider: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Save the fetched rates in the database
            for valuation_date, rates in fetched_rates.items():
                for exchanged_currency, rate_value in rates.items():
                    try:
                        exchanged_currency_obj = Currency.objects.get(code=exchanged_currency)
                        CurrencyExchangeRate.objects.update_or_create(
                            source_currency=Currency.objects.get(code=source_currency),
                            exchanged_currency=exchanged_currency_obj,
                            valuation_date=valuation_date,
                            defaults={"rate_value": rate_value},
                        )
                    except Currency.DoesNotExist:
                        logger.error(f"Currency '{exchanged_currency}' does not exist in the database.")
                        continue
                rates_data.append({"valuation_date": valuation_date, "rates": rates})

            return Response(rates_data, status=status.HTTP_200_OK)

        # Log invalid request data
        logger.warning(f"Invalid query parameters: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConvertAmountView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/currency/convert-amount/

    Authorization: token <token> (included in request headers)
    Content-Type: application/json

    Description:
    This API allows you to convert an amount from a source currency to a target currency.
    It takes the source currency, amount, and exchanged currency as required query parameters.
    Optionally, a provider name can be provided to fetch the exchange rate from a third-party provider.
    If no rate is found in the database, it attempts to fetch the rate from the specified provider.

    Query Parameters:
    - source_currency (str): The source currency code (e.g., USD).
    - amount (float): The amount to be converted.
    - exchanged_currency (str): The target currency code (e.g., INR).
    - provider_name (str, optional): The name of the provider (e.g., 'mock').
    """
    def get(self, request):
        # Log the request query parameters
        logger.info(f"Received request for currency conversion: {request.query_params}")

        # Validate incoming query parameters using the serializer
        serializer = ConvertAmountRequestSerializer(data=request.query_params)
        if serializer.is_valid():
            source_currency = serializer.validated_data["source_currency"]
            exchanged_currency = serializer.validated_data["exchanged_currency"]
            amount = serializer.validated_data["amount"]
            provider_name = serializer.validated_data.get("provider_name", None)

            try:
                amount = float(amount)
            except ValueError:
                logger.error(f"Invalid amount: {amount}. Amount must be a valid number.")
                return Response(
                    {"error": "Amount must be a valid number"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Try to fetch the latest rate from the database
            today = date.today()
            rate = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                exchanged_currency__code=exchanged_currency,
                valuation_date=today,
            ).first()

            # Log if rate is found in the database or needs to be fetched from provider
            if rate:
                logger.info(f"Rate found in database: {rate.rate_value}")
                rate_value = rate.rate_value
            else:
                logger.info(f"Rate not found in database, fetching from provider: {provider_name}")
                provider = ProviderFactory.get_provider_adapter(provider_name)
                try:
                    rate_value = provider.fetch_exchange_rate(
                        source_currency, exchanged_currency
                    )
                    # Log the fetched rate value
                    logger.info(f"Fetched rate from provider: {rate_value}")

                    # Save the fetched rate in the database
                    CurrencyExchangeRate.objects.update_or_create(
                        source_currency=Currency.objects.get(code=source_currency),
                        exchanged_currency=Currency.objects.get(
                            code=exchanged_currency
                        ),
                        valuation_date=today,
                        defaults={"rate_value": rate_value},
                    )
                except Exception as e:
                    logger.error(f"Error fetching exchange rate: {str(e)}")
                    return Response(
                        {"error": f"Failed to fetch exchange rate: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            # Calculate the converted amount
            converted_amount = amount * float(rate_value)

            # Log the result of the conversion
            logger.info(f"Conversion successful: {amount} {source_currency} = {converted_amount} {exchanged_currency}")

            return Response(
                {
                    "source_currency": source_currency,
                    "exchanged_currency": exchanged_currency,
                    "amount": amount,
                    "rate_value": rate_value,
                    "converted_amount": converted_amount,
                },
                status=status.HTTP_200_OK,
            )

        # Log invalid request data
        logger.warning(f"Invalid query parameters: {serializer.errors}")
        return Response(
            {"error": "Invalid query parameters"},
            status=status.HTTP_400_BAD_REQUEST,
        )