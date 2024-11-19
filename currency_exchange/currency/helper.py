from currency.models import Currency

def currency_exists(source_currency):
        """
        Helper function to check if the currency exists.
        """
        if not Currency.objects.filter(code=source_currency).exists():
            return False
        return True