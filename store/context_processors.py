"""Variables disponibles dans tous les templates."""

from django.conf import settings

from .cart import Cart
from .models import Category, Gender, Notification
from .wishlist import Wishlist


def store_globals(request):
    cart = Cart(request)
    wishlist = Wishlist(request)

    notif_unread = 0
    notif_recent = []
    if request.user.is_authenticated:
        user_notifs = Notification.objects.filter(user=request.user)
        notif_unread = user_notifs.filter(is_read=False).count()
        notif_recent = list(user_notifs[:8])

    return {
        "cart": cart,
        "cart_count": len(cart),
        "wishlist_ids": wishlist.product_ids(),
        "wishlist_count": len(wishlist),
        "currency": settings.DRESSIT_CURRENCY_SYMBOL,
        "notif_unread": notif_unread,
        "notif_recent": notif_recent,
        "nav_categories_homme": Category.objects.filter(
            gender__in=[Gender.HOMME, Gender.UNISEXE]
        )[:8],
        "nav_categories_femme": Category.objects.filter(
            gender__in=[Gender.FEMME, Gender.UNISEXE]
        )[:8],
    }
