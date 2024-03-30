# user/helpers.py
from django.db.models import signals
from django.dispatch import receiver
from django.db.models.signals import post_save
from user.models import User
from product.models import DailyRate, Products

@receiver(signals.post_save, sender=DailyRate)
def update_products_on_daily_rate_change(sender, instance, **kwargs):
    # Update all related products when a new DailyRate is created or updated
    related_products = Products.objects.all()
    for product in related_products:
        product.daily_rate = instance
        product.save()
