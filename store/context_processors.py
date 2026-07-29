"""Variables disponibles dans tous les templates."""

from django.conf import settings

from .cart import Cart
from .models import Category, Gender
from .wishlist import Wishlist


def store_globals(request):
    cart = Cart(request)
    wishlist = Wishlist(request)
    return {
        "cart": cart,
        "cart_count": len(cart),
        "wishlist_ids": wishlist.product_ids(),
        "wishlist_count": len(wishlist),
        "currency": settings.DRESSIT_CURRENCY_SYMBOL,
        "nav_categories_homme": Category.objects.filter(
            gender__in=[Gender.HOMME, Gender.UNISEXE]
        )[:8],
        "nav_categories_femme": Category.objects.filter(
            gender__in=[Gender.FEMME, Gender.UNISEXE]
        )[:8],
    }
