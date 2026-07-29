"""Envoi des e-mails transactionnels (confirmation de commande)."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_order_confirmation(order, request=None):
    """Envoie l'e-mail de confirmation au client.

    En développement (backend console), le message s'affiche dans le terminal.
    Ne lève jamais d'erreur bloquante pour l'utilisateur : en cas d'échec SMTP,
    la commande reste valide.
    """
    if not order.email:
        return False

    subject = _("Confirmation de votre commande DressIT #%(id)s") % {"id": order.id}
    context = {"order": order, "currency": settings.DRESSIT_CURRENCY_SYMBOL}
    text_body = render_to_string("emails/order_confirmation.txt", context, request=request)
    html_body = render_to_string("emails/order_confirmation.html", context, request=request)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:  # pragma: no cover - dépend de la config SMTP
        return False
