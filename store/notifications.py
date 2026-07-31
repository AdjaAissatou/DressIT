"""Notifications in-app (cloche 🔔) pour l'administrateur et les clients.

Chaque notification est une ligne par destinataire, avec son propre état
« lue / non lue ». Les notifications administrateur sont créées pour tous les
membres du personnel (is_staff) ; les notifications client pour le compte lié à
la commande / réclamation.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Notification


def _staff_users():
    return get_user_model().objects.filter(is_active=True, is_staff=True)


def push(user, kind, title, body="", url=""):
    """Crée une notification pour un utilisateur (ignore si user est None)."""
    if user is None:
        return None
    return Notification.objects.create(
        user=user, kind=kind, title=title, body=body, url=url
    )


def notify_admins(kind, title, body="", url=""):
    """Crée la même notification pour tous les membres du personnel."""
    notifs = [
        Notification(user=u, kind=kind, title=title, body=body, url=url)
        for u in _staff_users()
    ]
    if notifs:
        Notification.objects.bulk_create(notifs)
    return len(notifs)


# --------------------------------------------------------------------------- #
# Événements métier
# --------------------------------------------------------------------------- #
def notify_new_order(order, request=None):
    """Prévient l'administrateur d'une nouvelle commande (in-app + e-mail)."""
    if order.admin_notified:
        return
    url = reverse("manage_order_detail", args=[order.id])
    notify_admins(
        Notification.Kind.ORDER,
        f"Nouvelle commande #{order.id}",
        f"{order.full_name} · {order.item_count} article(s) · {order.total} "
        f"{__currency()}",
        url,
    )
    order.admin_notified = True
    order.save(update_fields=["admin_notified"])

    # Notifie aussi le client connecté qu'on a bien reçu sa commande.
    if order.user_id:
        push(
            order.user,
            Notification.Kind.ORDER,
            f"Commande #{order.id} enregistrée",
            "Merci ! Nous préparons votre commande.",
            reverse("order_detail", args=[order.id]),
        )

    from .emails import send_new_order_admin

    send_new_order_admin(order, request)


def notify_payment(order):
    """Prévient le client (et l'admin) qu'un paiement a été reçu."""
    notify_admins(
        Notification.Kind.PAYMENT,
        f"Paiement reçu — commande #{order.id}",
        f"{order.full_name} · {order.total} {__currency()}",
        reverse("manage_order_detail", args=[order.id]),
    )
    if order.user_id:
        push(
            order.user,
            Notification.Kind.PAYMENT,
            f"Paiement confirmé — commande #{order.id}",
            "Votre paiement a bien été reçu.",
            reverse("order_detail", args=[order.id]),
        )


def notify_status(order):
    """Prévient le client d'un changement de statut de sa commande."""
    if order.user_id:
        push(
            order.user,
            Notification.Kind.STATUS,
            f"Commande #{order.id} : {order.get_status_display()}",
            "",
            reverse("order_detail", args=[order.id]),
        )


def notify_new_complaint(complaint):
    """Prévient l'administrateur d'une nouvelle réclamation."""
    notify_admins(
        Notification.Kind.COMPLAINT,
        f"Nouvelle réclamation #{complaint.id}",
        f"{complaint.name} · {complaint.get_subject_display()}",
        reverse("manage_complaint_detail", args=[complaint.id]),
    )


def notify_complaint_reply(complaint):
    """Prévient le client qu'une réponse a été apportée à sa réclamation."""
    if complaint.user_id:
        push(
            complaint.user,
            Notification.Kind.REPLY,
            f"Réponse à votre réclamation #{complaint.id}",
            "Le service client vous a répondu.",
            reverse("account"),
        )


def __currency():
    from django.conf import settings

    return settings.DRESSIT_CURRENCY_SYMBOL
