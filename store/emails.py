"""E-mails transactionnels enrichis (HTML + texte) aux couleurs de DressIT.

En développement (backend console), les messages s'affichent dans le terminal.
En production, configurez le SMTP via les variables DRESSIT_EMAIL_*.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


def _admin_email():
    return getattr(settings, "DRESSIT_ADMIN_EMAIL", "") or settings.DEFAULT_FROM_EMAIL


def _send(subject, base, context, to, request=None):
    """Rend emails/{base}.txt + emails/{base}.html et envoie le message.

    Ne lève jamais d'erreur bloquante : un échec SMTP n'invalide pas l'action.
    """
    recipients = [to] if isinstance(to, str) else list(to)
    recipients = [r for r in recipients if r]
    if not recipients:
        return False
    ctx = {"currency": settings.DRESSIT_CURRENCY_SYMBOL, **context}
    text_body = render_to_string(f"emails/{base}.txt", ctx, request=request)
    html_body = render_to_string(f"emails/{base}.html", ctx, request=request)
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:  # pragma: no cover - dépend de la config SMTP
        return False


# --------------------------------------------------------------------------- #
# Commandes
# --------------------------------------------------------------------------- #
def send_order_confirmation(order, request=None):
    subject = f"Confirmation de votre commande DressIT #{order.id}"
    return _send(subject, "order_confirmation", {"order": order}, order.email, request)


def send_payment_confirmation(order, request=None):
    subject = f"Paiement reçu — commande DressIT #{order.id}"
    return _send(subject, "payment_confirmation", {"order": order}, order.email, request)


def send_order_status_update(order, request=None):
    subject = f"Votre commande DressIT #{order.id} : {order.get_status_display()}"
    return _send(subject, "order_status", {"order": order}, order.email, request)


# --------------------------------------------------------------------------- #
# Réclamations (SAV)
# --------------------------------------------------------------------------- #
def send_complaint_received(complaint, request=None):
    """Accusé de réception au client + notification à l'administrateur."""
    _send(
        f"Nous avons bien reçu votre réclamation #{complaint.id}",
        "complaint_ack",
        {"complaint": complaint},
        complaint.email,
        request,
    )
    _send(
        f"[DressIT] Nouvelle réclamation #{complaint.id} — {complaint.get_subject_display()}",
        "complaint_admin",
        {"complaint": complaint},
        _admin_email(),
        request,
    )
    return True


def send_complaint_response(complaint, request=None):
    """Envoie la réponse du service client au client."""
    if not complaint.responded_at:
        complaint.responded_at = timezone.now()
        complaint.save(update_fields=["responded_at"])
    return _send(
        f"Réponse à votre réclamation DressIT #{complaint.id}",
        "complaint_response",
        {"complaint": complaint},
        complaint.email,
        request,
    )
