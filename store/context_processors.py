"""Variables disponibles dans tous les templates."""

from django.conf import settings

from .cart import Cart
from .models import Category, Gender


def store_globals(request):
    cart = Cart(request)
    return {
        "cart": cart,
        "cart_count": len(cart),
        "currency": settings.DRESSIT_CURRENCY_SYMBOL,
        "nav_categories_homme": Category.objects.filter(
            gender__in=[Gender.HOMME, Gender.UNISEXE]
        )[:8],
        "nav_categories_femme": Category.objects.filter(
            gender__in=[Gender.FEMME, Gender.UNISEXE]
        )[:8],
    }
