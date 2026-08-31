"""
Custom exceptions for AI providers.
"""


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    
    def __init__(self, message: str, provider: str = "", code: int = 500):
        self.message = message
        self.provider = provider
        self.code = code
        super().__init__(f"[{provider}] {message}" if provider else message)


class AIProviderConfigError(AIProviderError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, provider: str = "", missing_fields: list = None):
        self.missing_fields = missing_fields or []
        super().__init__(message, provider, code=400)


class AIProviderAPIError(AIProviderError):
    """Exception for API errors."""
    
    def __init__(self, message: str, provider: str = "", status_code: int = 500):
        self.status_code = status_code
        super().__init__(message, provider, code=status_code)


class AIProviderQuotaError(AIProviderError):
    """Exception for rate limit/quota errors."""
    
    def __init__(self, message: str = "API quota exceeded", provider: str = "", retry_after: int = 0):
        self.retry_after = retry_after
        super().__init__(message, provider, code=429)


class AIProviderTimeoutError(AIProviderError):
    """Exception for timeout errors."""
    
    def __init__(self, message: str = "Request timeout", provider: str = ""):
        super().__init__(message, provider, code=408)


class AIProviderAuthenticationError(AIProviderError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", provider: str = ""):
        super().__init__(message, provider, code=401)
