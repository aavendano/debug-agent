"""
Store models for multi-tenant ecommerce platform.
"""
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.utils.text import slugify


class Store(TenantMixin):
    """
    Store model representing a tenant in the multi-tenant system.
    Each store has its own isolated data and AI configuration.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Name of the store"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier for the store"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores',
        help_text="User who owns this store"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the store"
    )
    theme = models.CharField(
        max_length=50,
        default="default",
        help_text="Visual theme for the store"
    )
    logo = models.ImageField(
        upload_to="store_logos/",
        null=True,
        blank=True,
        help_text="Store logo"
    )
    favicon = models.ImageField(
        upload_to="store_favicons/",
        null=True,
        blank=True,
        help_text="Store favicon"
    )
    
    # SEO default settings
    seo_default_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Default keywords for SEO"
    )
    default_meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Default meta title for pages"
    )
    default_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Default meta description for pages"
    )
    
    # Contact information
    email = models.EmailField(
        blank=True,
        help_text="Store contact email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Store contact phone"
    )
    address = models.TextField(
        blank=True,
        help_text="Store physical address"
    )
    
    # Social media
    social_media = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links (JSON object)"
    )
    
    # AI Provider Configuration
    ai_provider = models.CharField(
        max_length=20,
        default="mistral",
        choices=[
            ("mistral", "Mistral"),
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("custom", "Custom"),
        ],
        help_text="AI provider for content generation"
    )
    ai_api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        validators=[MinLengthValidator(10)],
        help_text="API key for the AI provider"
    )
    ai_base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Base URL for AI provider API (optional, for self-hosting)"
    )
    ai_model = models.CharField(
        max_length=50,
        default="mistral-tiny",
        help_text="Model to use for AI generation (e.g., mistral-tiny, gpt-4o-mini)"
    )
    ai_max_tokens = models.PositiveIntegerField(
        default=1000,
        help_text="Maximum tokens per AI request"
    )
    ai_temperature = models.FloatField(
        default=0.7,
        help_text="Temperature for AI generation (0-1)",
        validators=[models.MinValueValidator(0.0), models.MaxValueValidator(1.0)]
    )
    ai_auto_generate_seo = models.BooleanField(
        default=True,
        help_text="Automatically generate SEO content for products"
    )
    
    # Budget control
    ai_budget_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly budget for AI usage in USD"
    )
    ai_tokens_used_monthly = models.PositiveIntegerField(
        default=0,
        help_text="Tokens used in the current month"
    )
    ai_cost_used_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="Cost incurred in the current month in USD"
    )
    
    # Store status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the store is active"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether the store is publicly accessible"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the store was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the store was last updated"
    )
    
    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to generate slug if not provided."""
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the store."""
        from django.urls import reverse
        return reverse('store_detail', kwargs={'slug': self.slug})
    
    def get_ai_config(self):
        """Get AI configuration as a dictionary."""
        return {
            'provider': self.ai_provider,
            'api_key': self.ai_api_key,
            'base_url': self.ai_base_url,
            'model': self.ai_model,
            'max_tokens': self.ai_max_tokens,
            'temperature': self.ai_temperature,
        }
    
    def get_ai_provider(self):
        """Get an instance of the configured AI provider."""
        from ai_providers.factory import get_provider
        from ai_providers.base import AIConfig
        
        if not self.ai_api_key:
            return None
            
        config = AIConfig(
            api_key=self.ai_api_key,
            base_url=self.ai_base_url,
            model=self.ai_model,
            max_tokens=self.ai_max_tokens,
            temperature=self.ai_temperature,
        )
        
        try:
            return get_provider(self.ai_provider, config)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to get AI provider for store {self.id}: {e}")
            return None
    
    def can_use_ai(self) -> bool:
        """Check if the store can use AI (has valid API key and budget)."""
        if not self.ai_api_key:
            return False
        
        if self.ai_budget_monthly is None:
            return True
        
        return self.ai_cost_used_monthly < self.ai_budget_monthly
    
    def update_ai_usage(self, tokens: int, cost: float):
        """Update AI usage statistics."""
        self.ai_tokens_used_monthly += tokens
        self.ai_cost_used_monthly += cost
        self.save(update_fields=['ai_tokens_used_monthly', 'ai_cost_used_monthly'])
    
    def reset_ai_usage(self):
        """Reset monthly AI usage statistics."""
        self.ai_tokens_used_monthly = 0
        self.ai_cost_used_monthly = 0.0
        self.save(update_fields=['ai_tokens_used_monthly', 'ai_cost_used_monthly'])


class Domain(DomainMixin):
    """
    Domain model for multi-tenant support.
    Allows each store to have its own domain.
    """
    pass
