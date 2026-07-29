"""Signaux : e-mails automatiques lors des changements de statut de commande."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .emails import send_order_status_update
from .models import Order

# Statuts qui déclenchent un e-mail au client.
NOTIFY_STATUSES = {Order.Status.SHIPPED, Order.Status.DELIVERED, Order.Status.CANCELLED}


@receiver(pre_save, sender=Order)
def _stash_old_status(sender, instance, **kwargs):
    if instance.pk:
        old = Order.objects.filter(pk=instance.pk).only("status").first()
        instance._old_status = old.status if old else None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def _notify_status_change(sender, instance, created, **kwargs):
    if created:
        return
    old = getattr(instance, "_old_status", None)
    if old and old != instance.status and instance.status in NOTIFY_STATUSES:
        send_order_status_update(instance)
