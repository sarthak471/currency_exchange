from provider.models import Provider
from provider.providers.beacon import CurrencyBeaconProvider
from provider.providers.mock import MockProvider

class ProviderFactory:
    @staticmethod
    def get_provider_adapter(provider_name=None):
        """
        Factory method to return the appropriate provider adapter based on the name or priority.

        :param provider_name: Name of the provider (e.g., "currency_beacon"). If None, use the highest-priority active provider.
        :return: An instance of the appropriate provider adapter.
        """
        if provider_name:
            provider_instance = Provider.objects.filter(name=provider_name, active=True).first()
            if not provider_instance:
                raise ValueError(f"Provider '{provider_name}' is either inactive or does not exist.")
        else:
            # Get the highest-priority active provider
            provider_instance = Provider.objects.filter(active=True).order_by('priority').first()
            if not provider_instance:
                raise ValueError("No active providers found.")

        # Dynamically import the provider adapter based on the provider's name
        if provider_instance.name == "currency_beacon":
            return CurrencyBeaconProvider()
        elif provider_instance.name == "mock":
            return MockProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_instance.name}")
