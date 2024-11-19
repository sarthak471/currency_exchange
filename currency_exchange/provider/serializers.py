from rest_framework import serializers

from currency.helper import currency_exists

from provider.helper import provider_exists
from provider.models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name", "priority", "active"]


class HistoricalDataRequestSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3)
    provider_name = serializers.CharField(max_length=50)
    exchanged_currency = serializers.ListField(
        child=serializers.CharField(max_length=3)
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate_source_currency(self, value):
        """
        Custom validation for source_currency.
        Ensure the currency exists in the database.
        """
        if not currency_exists(value):
            raise serializers.ValidationError(
                f"Source Currency '{value}' does not exist."
            )
        return value

    def validate_exchanged_currency(self, value):
        missing_currencies = []
        for currency in value:
            if not currency_exists(currency):
                missing_currencies.append(currency)
        if missing_currencies:
            raise serializers.ValidationError(
                f"The following currencies do not exist: {', '.join(missing_currencies)}"
            )
        return value

    def validate_provider_name(self, value):
        """
        Custom validation for provider_name.
        Ensure the provider exists in the database if provided.
        """
        if value and not provider_exists(value):
            raise serializers.ValidationError(
                f"Provider '{value}' is either inactive or does not exist."
            )
        return value

    def validate(self, data):
        """
        Validates that end_date is not earlier than start_date.
        """
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be earlier than start date."}
            )
        return data
