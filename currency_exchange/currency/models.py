from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.code} - {self.name}"


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(
        Currency, related_name="source_currency_rates", on_delete=models.CASCADE
    )
    exchanged_currency = models.ForeignKey(
        Currency, related_name="exchanged_currency_rates", on_delete=models.CASCADE
    )
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(
        max_digits=18, decimal_places=6, db_index=True
    )  # Exchange rate value

    class Meta:
        unique_together = ("source_currency", "exchanged_currency", "valuation_date")
        indexes = [
            models.Index(fields=["valuation_date"]),
            models.Index(fields=["source_currency", "exchanged_currency"]),
        ]

    def __str__(self):
        return f"{self.source_currency} -> {self.exchanged_currency} on {self.valuation_date}: {self.rate_value}"
