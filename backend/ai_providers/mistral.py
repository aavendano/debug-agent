"""
Mistral AI provider implementation.
"""
from typing import Optional, Dict, Any
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from .base import AIProvider, AIConfig, AIResponse, ProviderStatus
from .exceptions import (
    AIProviderConfigError,
    AIProviderAPIError,
    AIProviderQuotaError,
    AIProviderTimeoutError,
    AIProviderAuthenticationError
)
import httpx


class MistralProvider(AIProvider):
    """AI provider for Mistral API."""
    
    PROVIDER_NAME = "mistral"
    
    # Pricing per token (USD) - Update according to Mistral's official rates
    PRICING = {
        "mistral-tiny": {"input": 0.00000025, "output": 0.00000025},
        "mistral-small": {"input": 0.0000007, "output": 0.0000007},
        "mistral-medium": {"input": 0.0000027, "output": 0.0000027},
        "mistral-large": {"input": 0.000008, "output": 0.000008},
        "codestral-latest": {"input": 0.000003, "output": 0.000003},
        "mistral-embed": {"input": 0.0000001, "output": 0.0},
    }
    
    SUPPORTED_MODELS = [
        "mistral-tiny",
        "mistral-small", 
        "mistral-medium",
        "mistral-large",
        "codestral-latest",
        "mistral-embed",
    ]
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
    
    def _initialize_client(self):
        """Initialize Mistral client."""
        self.client = MistralClient(
            api_key=self.config.api_key,
            endpoint=self.config.base_url or "https://api.mistral.ai/v1",
            timeout=self.config.timeout,
        )
    
    def validate_config(self) -> bool:
        """Validate Mistral configuration."""
        if not self.config.api_key:
            raise AIProviderConfigError(
                "Mistral API key is required",
                provider=self.PROVIDER_NAME,
                missing_fields=["api_key"]
            )
        
        if self.config.model and self.config.model not in self.SUPPORTED_MODELS:
            raise AIProviderConfigError(
                f"Model '{self.config.model}' is not supported by Mistral. "
                f"Supported models: {', '.join(self.SUPPORTED_MODELS)}",
                provider=self.PROVIDER_NAME,
                missing_fields=["model"]
            )
        
        return True
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        Generate text using Mistral API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system message
            **kwargs: Additional parameters (max_tokens, temperature, etc.)
            
        Returns:
            AIResponse with generated text
        """
        # Merge config with kwargs
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        temperature = kwargs.get('temperature', self.config.temperature)
        
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))
        
        try:
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in kwargs.items() if k not in ['max_tokens', 'temperature']}
            )
            
            choice = response.choices[0]
            content = choice.message.content
            finish_reason = choice.finish_reason
            
            # Estimate tokens used (Mistral doesn't always return usage)
            input_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)
            output_tokens = len(content.split())
            total_tokens = input_tokens + output_tokens
            
            cost = self.get_cost(total_tokens)
            
            return AIResponse(
                content=content,
                model=self.config.model,
                tokens_used=total_tokens,
                cost=cost,
                provider=self.PROVIDER_NAME,
                finish_reason=finish_reason,
                status=ProviderStatus.AVAILABLE
            )
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = str(e)
            
            if status_code == 401:
                raise AIProviderAuthenticationError(
                    "Invalid Mistral API key",
                    provider=self.PROVIDER_NAME
                )
            elif status_code == 429:
                retry_after = int(e.response.headers.get('retry-after', 60))
                raise AIProviderQuotaError(
                    "Mistral API rate limit exceeded",
                    provider=self.PROVIDER_NAME,
                    retry_after=retry_after
                )
            elif status_code == 408:
                raise AIProviderTimeoutError(
                    "Mistral API request timeout",
                    provider=self.PROVIDER_NAME
                )
            else:
                raise AIProviderAPIError(
                    f"Mistral API error: {error_detail}",
                    provider=self.PROVIDER_NAME,
                    status_code=status_code
                )
                
        except httpx.TimeoutException:
            raise AIProviderTimeoutError(
                "Request to Mistral API timed out",
                provider=self.PROVIDER_NAME
            )
            
        except Exception as e:
            raise AIProviderAPIError(
                f"Unexpected error with Mistral API: {str(e)}",
                provider=self.PROVIDER_NAME
            )
    
    def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        Generate JSON output using Mistral API.
        
        Args:
            prompt: User prompt
            schema: Optional JSON schema (not directly used by Mistral, but for documentation)
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with JSON content
        """
        kwargs['response_format'] = {"type": "json_object"}
        return self.generate_text(prompt, **kwargs)
    
    def check_health(self) -> ProviderStatus:
        """Check Mistral API health."""
        try:
            # Make a minimal request to test connectivity
            test_response = self.generate_text(
                prompt="Respond with just 'OK' if you are working.",
                max_tokens=5,
                temperature=0.0
            )
            if "OK" in test_response.content:
                return ProviderStatus.AVAILABLE
            return ProviderStatus.AVAILABLE  # API is reachable
        except AIProviderQuotaError:
            return ProviderStatus.RATE_LIMITED
        except AIProviderAuthenticationError:
            return ProviderStatus.UNAVAILABLE
        except Exception:
            return ProviderStatus.UNAVAILABLE
