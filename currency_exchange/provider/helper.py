from .models import Provider

def provider_exists(provider_name):
        """
        Helper function to check if the provider exists and is active.
        """
        provider_instance = Provider.objects.filter(name=provider_name, active=True).first()
        if not provider_instance:
            return False
        return provider_instance