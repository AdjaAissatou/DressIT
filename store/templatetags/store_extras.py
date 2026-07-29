"""Filtres de gabarit de la boutique."""

from decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings

register = template.Library()

NBSP = " "  # espace insécable


@register.filter
def money(value, with_symbol=True):
    """Formate un montant en Franc CFA : 15900 -> « 15 900 FCFA ».

    Les montants sont affichés en nombres entiers (le FCFA n'a pas de centimes),
    avec une espace insécable comme séparateur de milliers.
    """
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value
    rounded = int(amount.to_integral_value(rounding="ROUND_HALF_UP"))
    formatted = f"{rounded:,}".replace(",", NBSP)
    if with_symbol:
        return f"{formatted}{NBSP}{settings.DRESSIT_CURRENCY_SYMBOL}"
    return formatted
