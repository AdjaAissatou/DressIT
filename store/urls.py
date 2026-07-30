"""URLs de la boutique DressIT."""

from django.urls import path

from . import staff, views
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
    # Recherche par photo
    path("recherche-photo/", views.photo_search, name="photo_search"),
    # Commande
    path("commander/", views.checkout, name="checkout"),
    path(
        "commande/<int:order_id>/confirmation/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    # Paiement (retours & webhooks Wave / Orange Money)
    path("paiement/<int:order_id>/retour/", views.payment_return, name="payment_return"),
    path("paiement/<int:order_id>/annule/", views.payment_cancel, name="payment_cancel"),
    path("paiement/wave/webhook/", views.wave_webhook, name="wave_webhook"),
    path("paiement/orange/webhook/", views.om_webhook, name="om_webhook"),
    # Espace client
    path("compte/", views.account, name="account"),
    path("compte/commande/<int:order_id>/", views.order_detail, name="order_detail"),
    path("inscription/", views.signup, name="signup"),
    # Réclamations (SAV)
    path("reclamation/", views.complaint_create, name="complaint"),
    # Gestion (staff)
    path("gestion/", staff.dashboard, name="dashboard"),
    path("gestion/studio-ia/", staff.ai_studio, name="ai_studio"),
    # Back-office : articles
    path("gestion/articles/", staff.product_list, name="manage_products"),
    path("gestion/articles/nouveau/", staff.product_edit, name="manage_product_add"),
    path("gestion/articles/<int:pk>/", staff.product_edit, name="manage_product_edit"),
    path("gestion/articles/<int:pk>/supprimer/", staff.product_delete, name="manage_product_delete"),
    # Back-office : catégories
    path("gestion/categories/", staff.category_list, name="manage_categories"),
    path("gestion/categories/nouvelle/", staff.category_edit, name="manage_category_add"),
    path("gestion/categories/<int:pk>/", staff.category_edit, name="manage_category_edit"),
    path("gestion/categories/<int:pk>/supprimer/", staff.category_delete, name="manage_category_delete"),
]
