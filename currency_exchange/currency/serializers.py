from datetime import datetime

from rest_framework import serializers

from currency.models import Currency
from currency.helper import currency_exists

from provider.helper import provider_exists


class CurrencyRatesListRequestSerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    provider_name = serializers.CharField(max_length=100, required=False)

    def validate_source_currency(self, value):
        """
        Custom validation for source_currency.
        Ensure the currency exists in the database.
        """
        if not currency_exists(value):
            raise serializers.ValidationError(f"Currency '{value}' does not exist.")
        return value

    def validate_provider_name(self, value):
        """
        Custom validation for provider_name.
        Ensure the provider exists in the database.
        """
        if value and not provider_exists(value):
            raise serializers.ValidationError(
                f"Provider '{value}' is either inactive or does not exist."
            )
        return value

    def validate_start_date(self, value):
        """
        Custom validation for start_date.
        Ensure start_date is not in the future.
        """
        if value > datetime.today().date():
            raise serializers.ValidationError("start_date cannot be in the future.")
        return value

    def validate_end_date(self, value):
        """
        Custom validation for end_date.
        Ensure end_date is not in the future.
        """
        if value > datetime.today().date():
            raise serializers.ValidationError("end_date cannot be in the future.")
        return value

    def validate(self, data):
        """
        Custom validation to ensure start_date is not after end_date.
        """
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    "start_date cannot be after end_date."
                )

        return data


class ConvertAmountRequestSerializer(serializers.Serializer):
    source_currency = serializers.CharField(required=True)
    exchanged_currency = serializers.CharField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    provider_name = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Optional. Name of the provider to use. Defaults to the provider with the highest priority.",
    )

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
        """
        Custom validation for exchanged_currency.
        Ensure the exchanged currency exists in the database.
        """
        if not currency_exists(value):
            raise serializers.ValidationError(
                f"Exchanged currency '{value}' does not exist."
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

    def validate_amount(self, value):
        """
        Custom validation for amount.
        Ensure the amount is a positive value.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"

class ConvertAmountSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3)
    target_currency = serializers.ListField(
        child=serializers.CharField(max_length=3)
    )
    amount = serializers.FloatField()
    provider_name = serializers.CharField(max_length=50, required=False)

    def validate_amount(self, value):
        """
        Ensure the amount is greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("The amount must be greater than zero.")
        return value