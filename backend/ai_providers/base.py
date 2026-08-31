"""
Base classes and data structures for AI providers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ProviderStatus(Enum):
    """Status of an AI provider."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    tokens_used: int = 0
    cost: float = 0.0  # Estimated cost in USD
    provider: str = ""
    status: ProviderStatus = ProviderStatus.AVAILABLE
    finish_reason: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.error_message:
            self.status = ProviderStatus.ERROR


@dataclass
class AIConfig:
    """Configuration for an AI provider."""
    api_key: str
    base_url: Optional[str] = None
    model: str = "default"
    timeout: int = 30
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[list] = None
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    # Pricing information (to be overridden by subclasses)
    PRICING: Dict[str, Dict[str, float]] = {
        "default": {"input": 0.0, "output": 0.0}
    }
    
    # Supported models
    SUPPORTED_MODELS: list = []
    
    # Provider name
    PROVIDER_NAME: str = "base"
    
    def __init__(self, config: AIConfig):
        """
        Initialize the AI provider with configuration.
        
        Args:
            config: AIConfig instance with provider settings
        """
        self.config = config
        self.validate_config()
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the API client for the provider."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            AIProviderConfigError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse: The generated response
        """
        pass
    
    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        Generate JSON-structured output from a prompt.
        
        Args:
            prompt: The user prompt
            schema: Optional JSON schema for response structure
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse: The generated response with JSON content
        """
        pass
    
    def get_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            tokens: Number of tokens
            model: Model name (uses config.model if not provided)
            
        Returns:
            float: Cost in USD
        """
        model = model or self.config.model
        pricing = self.PRICING.get(model, self.PRICING.get("default", {"input": 0.0, "output": 0.0}))
        return tokens * (pricing.get("input", 0.0) + pricing.get("output", 0.0)) / 2
    
    def get_name(self) -> str:
        """Get the provider name."""
        return self.PROVIDER_NAME
    
    def get_supported_models(self) -> list:
        """Get list of supported models."""
        return self.SUPPORTED_MODELS
    
    def check_health(self) -> ProviderStatus:
        """
        Check if the provider API is healthy.
        
        Returns:
            ProviderStatus: Current status of the provider
        """
        try:
            # Try a simple request to check connectivity
            test_response = self.generate_text(
                prompt="Say 'OK' if you are working.",
                max_tokens=5
            )
            if test_response.content.strip().upper() == "OK":
                return ProviderStatus.AVAILABLE
            return ProviderStatus.AVAILABLE  # Even if not OK, API is reachable
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str:
                return ProviderStatus.RATE_LIMITED
            return ProviderStatus.UNAVAILABLE
