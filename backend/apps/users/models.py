"""
User models for ecommerce platform.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator


class User(AbstractUser):
    """
    Custom user model for the ecommerce platform.
    Extends Django's AbstractUser with additional fields.
    """
    
    # Remove username from AbstractUser and use email as the identifier
    username = None
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator(message=_('Enter a valid email address.'))],
        help_text=_('Required. Must be a valid email address.')
    )
    
    # Personal information
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True,
        help_text=_('Your first name')
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True,
        help_text=_('Your last name')
    )
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('Your contact phone number')
    )
    
    # Address
    address = models.TextField(
        _('address'),
        blank=True,
        help_text=_('Your physical address')
    )
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
        help_text=_('Your city')
    )
    state = models.CharField(
        _('state'),
        max_length=100,
        blank=True,
        help_text=_('Your state or province')
    )
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        default='ES',
        help_text=_('Your country')
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20,
        blank=True,
        help_text=_('Your postal or ZIP code')
    )
    
    # Profile information
    avatar = models.ImageField(
        _('avatar'),
        upload_to='user_avatars/',
        null=True,
        blank=True,
        help_text=_('Your profile picture')
    )
    bio = models.TextField(
        _('biography'),
        blank=True,
        help_text=_('A brief description about yourself')
    )
    
    # Preferences
    language = models.CharField(
        _('language'),
        max_length=10,
        default='es',
        help_text=_('Your preferred language')
    )
    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='UTC',
        help_text=_('Your timezone')
    )
    
    # Business information (for store owners)
    is_store_owner = models.BooleanField(
        _('is store owner'),
        default=False,
        help_text=_('Designates whether this user can own stores')
    )
    business_name = models.CharField(
        _('business name'),
        max_length=100,
        blank=True,
        help_text=_('Your business name')
    )
    tax_id = models.CharField(
        _('tax ID'),
        max_length=50,
        blank=True,
        help_text=_('Your tax identification number')
    )
    
    # Social media
    social_media = models.JSONField(
        _('social media'),
        default=dict,
        blank=True,
        help_text=_('Your social media profiles (JSON object)')
    )
    
    # Account status
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email.')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the user was created')
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the user was last updated')
    )
    
    # Set email as the USERNAME_FIELD
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_store_owner']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def get_avatar_url(self):
        """Get the URL for the user's avatar."""
        if self.avatar:
            return self.avatar.url
        # Return a default avatar URL
        return f"https://ui-avatars.com/api/?name={self.get_full_name()}&background=random"
    
    def get_social_media_links(self):
        """Get social media links as a dictionary."""
        return self.social_media or {}
    
    def can_create_store(self) -> bool:
        """Check if the user can create a new store."""
        return self.is_store_owner and self.is_active
    
    def get_owned_stores(self):
        """Get all stores owned by this user."""
        from apps.stores.models import Store
        return Store.objects.filter(owner=self)
    
    def get_active_stores(self):
        """Get all active stores owned by this user."""
        return self.get_owned_stores().filter(is_active=True)
