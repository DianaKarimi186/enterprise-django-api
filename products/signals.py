from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Product


INVENTORY_CACHE_KEY = "inventory_products"


@receiver(post_save, sender=Product)
def invalidate_product_cache_on_save(sender, instance, **kwargs):
    cache.delete(INVENTORY_CACHE_KEY)


@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    cache.delete(INVENTORY_CACHE_KEY)