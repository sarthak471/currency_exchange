import logging
import asyncio
from asgiref.sync import sync_to_async
from concurrent.futures import ThreadPoolExecutor
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProviderSerializer, HistoricalDataRequestSerializer
from .models import Provider
from .task.load_data import load_historical_data

logger = logging.getLogger("django")

class HealthCheckView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/provider/health-check

    Content-Type: application/json

    Description:
    This endpoint checks the health of the application by returning a success status and a message indicating that the application is running smoothly.
    This endpoint does not require any request body.
    """
    def get(self, request, *args, **kwargs):
        logger.info("Health check initiated.")

        data = {
            "status": "healthy",
            "message": "Application is running smoothly.",
        }
        return Response(data, status=status.HTTP_200_OK)


class ProviderView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/provider/list

    Content-Type: application/json

    Description:
    This endpoint retrieves a list of all providers from the database and returns them in the response body.
    This function does not require any request body.
    """
    def get(self, request):
        """
        Fetch all providers and return a list of them.

        :return: JSON response with a list of all providers.
        """
        try:
            logger.info("Fetching all providers.")
            providers = Provider.objects.all()

            # Serialize the data
            serializer = ProviderSerializer(providers, many=True)

            logger.info(f"Successfully fetched {len(providers)} providers.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching providers: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProviderPriorityUpdateView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/provider/update-priority

    Content-Type: application/json

    Expected request body (example):
    {
        "name": "ProviderA",  # The name of the provider to update
        "priority": 2  # The new priority value to assign
    }

    Description:
    This endpoint allows you to update the priority of a specific provider.
    The provider's name is provided in the request body, along with the new priority value.
    If another provider already has the same priority, the system will automatically adjust the conflicting provider's priority.
    """
    def patch(self, request):
        logger.info("Attempting to update provider priority.")

        # Validate input
        name = request.data.get("name")
        priority = request.data.get("priority")

        if not name or priority is None:
            logger.warning("Missing 'name' or 'priority' in request data.")
            return Response(
                {"error": "Both 'name' and 'priority' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            priority = int(priority)
        except ValueError:
            logger.warning(f"Invalid priority value: {priority}. Must be an integer.")
            return Response(
                {"error": "'priority' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the provider to update
            provider = Provider.objects.get(name=name)

            # Check if another provider has the same priority
            conflicting_provider = Provider.objects.filter(priority=priority).exclude(id=provider.id).first()
            if conflicting_provider:
                logger.info(f"Adjusting priority for conflicting provider: {conflicting_provider.name}.")
                conflicting_provider.priority += 1
                conflicting_provider.save()

            # Update the priority of the requested provider
            provider.priority = priority
            provider.save()

            logger.info(f"Provider '{provider.name}' priority updated to {provider.priority}.")
            return Response(
                {"message": "Provider priority updated successfully!", "provider": {
                    "id": provider.id,
                    "name": provider.name,
                    "priority": provider.priority,
                    "active": provider.active,
                }},
                status=status.HTTP_200_OK
            )

        except Provider.DoesNotExist:
            logger.warning(f"Provider with name '{name}' not found.")
            return Response(
                {"error": f"Provider with name '{name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating provider priority: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HistoricalDataLoaderView(APIView):
    """
    Endpoint: http://127.0.0.1:8000/mycurrency/provider/load-historical-data

    Content-Type: application/json

    Expected request body (example):
    {
        "source_currency": "USD",
        "provider_name": "",
        "exchanged_currency": "EUR",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }

    Description:
    This endpoint triggers the process of loading historical data from a given provider.
    The user must provide relevant data including the source currency, the exchanged currency, the provider name, and the date range (start and end dates).
    This request will initiate an asynchronous task to load the historical data, which is processed in the background.
    """
    executor = ThreadPoolExecutor(max_workers=5)

    def post(self, request, *args, **kwargs):
        logger.info("Historical data loading request received.")

        serializer = HistoricalDataRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            source_currency = data["source_currency"]
            provider_name = data["provider_name"]
            exchanged_currency = data["exchanged_currency"]
            start_date = data["start_date"]
            end_date = data["end_date"]

            logger.info(f"Validated data: source_currency={source_currency}, provider_name={provider_name}, "
                        f"exchanged_currency={exchanged_currency}, start_date={start_date}, end_date={end_date}")

            try:
                def run_async_task():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        load_historical_data(
                            provider_name,
                            source_currency,
                            exchanged_currency,
                            str(start_date),
                            str(end_date)
                        )
                    )
                    loop.close()
                    return result

                # Execute the async function in a separate thread
                future = self.executor.submit(run_async_task)

                logger.info("Historical data loading task started.")
                return Response(
                    {"message": "Historical data loading started."},
                    status=status.HTTP_202_ACCEPTED
                )
            except Exception as e:
                logger.error(f"Error initiating historical data loading: {str(e)}")
                return Response(
                    {"error": f"An unexpected error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.warning(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
