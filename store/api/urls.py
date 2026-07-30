"""Routes de l'API REST DressIT (préfixe /api/)."""

from django.urls import path

from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="api_register"),
    path("auth/login/", views.login_view, name="api_login"),
    path("auth/me/", views.me_view, name="api_me"),
    # Catalogue
    path("config/", views.config_view, name="api_config"),
    path("categories/", views.CategoryList.as_view(), name="api_categories"),
    path("products/", views.ProductList.as_view(), name="api_products"),
    path("products/search-photo/", views.PhotoSearchView.as_view(), name="api_photo_search"),
    path("products/<slug:slug>/", views.ProductDetail.as_view(), name="api_product"),
    # Favoris
    path("wishlist/", views.WishlistView.as_view(), name="api_wishlist"),
    # Promo
    path("promo/validate/", views.promo_validate, name="api_promo"),
    # Commandes
    path("orders/", views.OrderList.as_view(), name="api_orders"),
    path("orders/create/", views.OrderCreateView.as_view(), name="api_order_create"),
    path("orders/<int:pk>/", views.OrderDetail.as_view(), name="api_order"),
    # Réclamations
    path("complaints/", views.ComplaintListCreate.as_view(), name="api_complaints"),
]
