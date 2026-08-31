"""
Factory for creating AI provider instances.
"""
from typing import Dict, Type, Optional
from .base import AIProvider, AIConfig
from .mistral import MistralProvider
from .exceptions import AIProviderError
import importlib
import logging

logger = logging.getLogger(__name__)

# Registry of available providers
# Format: {"provider_name": ProviderClass}
_PROVIDER_REGISTRY: Dict[str, Type[AIProvider]] = {
    "mistral": MistralProvider,
    # Add other built-in providers here
}


def register_provider(provider_name: str, provider_class: Type[AIProvider]):
    """
    Register a new AI provider dynamically.
    
    Args:
        provider_name: Name to register the provider under
        provider_class: Class implementing AIProvider
    """
    if not issubclass(provider_class, AIProvider):
        raise ValueError(f"{provider_class.__name__} must be a subclass of AIProvider")
    
    _PROVIDER_REGISTRY[provider_name] = provider_class
    logger.info(f"Registered AI provider: {provider_name}")


def get_provider(
    provider_name: str,
    config: AIConfig,
    default: Optional[str] = None
) -> AIProvider:
    """
    Get an instance of an AI provider.
    
    Args:
        provider_name: Name of the provider (e.g., "mistral", "openai")
        config: Configuration for the provider
        default: Default provider to use if specified provider is not found
        
    Returns:
        Instance of the requested AIProvider
        
    Raises:
        AIProviderError: If provider is not found or cannot be instantiated
    """
    # Try to get from registry
    provider_class = _PROVIDER_REGISTRY.get(provider_name)
    
    # If not found, try to import dynamically
    if provider_class is None:
        try:
            module_name = f"ai_providers.{provider_name}"
            module = importlib.import_module(module_name)
            # Look for a class named {ProviderName}Provider
            provider_class_name = f"{provider_name.capitalize()}Provider"
            provider_class = getattr(module, provider_class_name, None)
            if provider_class is None:
                # Try to find any AIProvider subclass
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) 
                        and issubclass(attr, AIProvider) 
                        and attr != AIProvider
                    ):
                        provider_class = attr
                        _PROVIDER_REGISTRY[provider_name] = provider_class
                        break
        except ImportError as e:
            logger.warning(f"Could not import provider {provider_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading provider {provider_name}: {e}")
    
    # If still not found, try default
    if provider_class is None:
        if default:
            return get_provider(default, config)
        available = ", ".join(get_available_providers())
        raise AIProviderError(
            f"AI provider '{provider_name}' not found. "
            f"Available providers: {available}. "
            f"Use register_provider() to add custom providers."
        )
    
    # Create and return instance
    try:
        return provider_class(config)
    except Exception as e:
        raise AIProviderError(
            f"Failed to initialize provider '{provider_name}': {str(e)}"
        )


def get_available_providers() -> list:
    """
    Get list of available provider names.
    
    Returns:
        List of registered provider names
    """
    return list(_PROVIDER_REGISTRY.keys())


def get_provider_class(provider_name: str) -> Type[AIProvider]:
    """
    Get the provider class without instantiating it.
    
    Args:
        provider_name: Name of the provider
        
    Returns:
        The provider class
        
    Raises:
        AIProviderError: If provider is not found
    """
    provider_class = _PROVIDER_REGISTRY.get(provider_name)
    if provider_class is None:
        raise AIProviderError(f"Provider '{provider_name}' not found")
    return provider_class


def create_provider_from_store(store) -> AIProvider:
    """
    Create an AI provider instance from a Store model.
    
    Args:
        store: Store instance with AI configuration
        
    Returns:
        Configured AIProvider instance
    """
    from ai_providers.base import AIConfig
    
    config = AIConfig(
        api_key=store.ai_api_key or "",
        base_url=store.ai_base_url,
        model=store.ai_model,
        max_tokens=store.ai_max_tokens,
        temperature=store.ai_temperature,
    )
    
    return get_provider(store.ai_provider, config)
