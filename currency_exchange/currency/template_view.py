import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic.base import View
from rest_framework.exceptions import ValidationError

from currency.models import Currency
from currency.serializers import ConvertAmountSerializer

from provider.models import Provider

import logging

logger = logging.getLogger(__name__)

class BackOfficeDashboardView(View):

    def get(self, request):
        currencies = Currency.objects.all()
        providers = Provider.objects.all()
        return render(
            request,
            "backoffice_dashboard.html",
            {"currencies": currencies,"providers":providers},
        )

    def post(self, request):
        serializer = ConvertAmountSerializer(data=request.POST)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return JsonResponse({"error": e.detail}, status=400)

        source_currency = serializer.validated_data['source_currency']
        target_currencies = serializer.validated_data['target_currency']
        amount = serializer.validated_data['amount']
        provider_name = serializer.validated_data.get('provider_name', 'currency_beacon')

        api_endpoint = "http://127.0.0.1:8000/mycurrency/currency/convert-amount/"
        results = {}

        for target_currency in target_currencies:
            params = {
                'source_currency': source_currency,
                'amount': amount,
                'exchanged_currency': target_currency,
                'provider_name': provider_name,
            }

            try:
                response = requests.get(api_endpoint, params=params)
                response_data = response.json()

                if response.status_code == 200 and 'converted_amount' in response_data:
                    results[target_currency] = response_data['converted_amount']
                else:
                    results[target_currency] = "Conversion failed"
            except requests.RequestException as e:
                results[target_currency] = f"Error: {e}"

        return JsonResponse({"converted_data": results})