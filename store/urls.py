"""URLs de la boutique DressIT."""

from django.urls import path

from . import views
from .models import Gender

urlpatterns = [
    path("", views.home, name="home"),
    # Rayons
    path("boutique/", views.product_list, name="shop"),
    path(
        "homme/",
        views.product_list,
        {"gender": Gender.HOMME},
        name="shop_homme",
    ),
    path(
        "femme/",
        views.product_list,
        {"gender": Gender.FEMME},
        name="shop_femme",
    ),
    path("categorie/<slug:slug>/", views.category_detail, name="category"),
    path("article/<slug:slug>/", views.product_detail, name="product"),
    # Panier
    path("panier/", views.cart_detail, name="cart"),
    path("panier/ajouter/<int:product_id>/", views.cart_add, name="cart_add"),
    path("panier/modifier/<str:key>/", views.cart_update, name="cart_update"),
    path("panier/retirer/<str:key>/", views.cart_remove, name="cart_remove"),
    path("panier/code-promo/", views.promo_apply, name="promo_apply"),
    path("panier/code-promo/retirer/", views.promo_remove, name="promo_remove"),
    # Favoris
    path("favoris/", views.wishlist_detail, name="wishlist"),
    path("favoris/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    # Commande
    path("commander/", views.checkout, name="checkout"),
    path(
        "commande/<int:order_id>/confirmation/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    # Espace client
    path("compte/", views.account, name="account"),
    path("compte/commande/<int:order_id>/", views.order_detail, name="order_detail"),
    path("inscription/", views.signup, name="signup"),
]
