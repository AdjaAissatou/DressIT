#!/usr/bin/env python3
"""Génère le catalogue de traduction anglais (locale/en) sans dépendre de gettext.

L'environnement ne dispose pas de l'outil `msgfmt` (paquet gettext), donc on
utilise `polib` pour écrire directement les fichiers .po ET .mo.

Usage :  python3 compile_translations.py

Pour ajouter/modifier une traduction : éditez le dictionnaire TRANSLATIONS
ci-dessous (clé = texte français exact, valeur = traduction anglaise) puis
relancez ce script.
"""

from pathlib import Path

import polib

BASE_DIR = Path(__file__).resolve().parent
PO_PATH = BASE_DIR / "locale" / "en" / "LC_MESSAGES" / "django.po"

# Français (msgid)  ->  Anglais (msgstr)
TRANSLATIONS = {
    # Navigation & global
    "Femme": "Women",
    "Homme": "Men",
    "Unisexe": "Unisex",
    "Tout voir": "Shop all",
    "Boutique": "Shop",
    "Nouveautés": "New arrivals",
    "Mon compte": "My account",
    "Connexion": "Log in",
    "Déconnexion": "Log out",
    "Panier": "Cart",
    "Langue": "Language",
    "Changer de thème": "Switch theme",
    "Créer un compte": "Create account",
    "Accueil": "Home",
    "Aide": "Help",
    "Livraison": "Shipping",
    "Retours": "Returns",
    "Contact": "Contact",
    "Tous droits réservés.": "All rights reserved.",
    "Mes commandes": "My orders",
    "Mon panier": "My cart",
    "DressIT — mode Homme & Femme aux prix les plus abordables.":
        "DressIT — Men's & Women's fashion at the most affordable prices.",
    "La mode Homme & Femme aux prix les plus abordables. Élégance, qualité et petits prix.":
        "Men's & Women's fashion at the most affordable prices. Elegance, quality and low prices.",
    # Accueil
    "Nouvelle collection": "New collection",
    "L'élégance à petit prix": "Elegance at a small price",
    "Découvrez notre sélection Homme & Femme : des pièces raffinées, une qualité soignée et les prix les plus abordables du marché.":
        "Discover our Men's & Women's selection: refined pieces, careful quality and the most affordable prices on the market.",
    "Collection Femme": "Women's collection",
    "Collection Homme": "Men's collection",
    "Prix les plus abordables — satisfaction garantie": "Most affordable prices — satisfaction guaranteed",
    "Rayon Femme": "Women's department",
    "Rayon Homme": "Men's department",
    "Trouvez votre style": "Find your style",
    "Le vestiaire masculin": "The men's wardrobe",
    "Voir tout": "See all",
    "Coups de cœur": "Favourites",
    "Notre sélection du moment": "Our current selection",
    "Bons plans": "Great deals",
    "Des prix encore plus doux": "Even sweeter prices",
    "Fraîchement arrivés": "Freshly arrived",
    "La boutique se prépare": "The shop is getting ready",
    "Aucun article pour le moment. Ajoutez vos produits depuis l'administration.":
        "No items yet. Add your products from the admin panel.",
    # Listes / filtres
    "Recherche": "Search",
    "Rechercher…": "Search…",
    "Rechercher": "Search",
    "Catégories": "Categories",
    "Toutes": "All",
    "article(s)": "item(s)",
    "Plus récents": "Most recent",
    "Prix croissant": "Price: low to high",
    "Prix décroissant": "Price: high to low",
    "Nom (A-Z)": "Name (A-Z)",
    "Aucun article trouvé": "No items found",
    "Essayez de modifier votre recherche ou vos filtres.": "Try changing your search or filters.",
    # Produit
    "Épuisé": "Sold out",
    "En stock": "In stock",
    "Taille": "Size",
    "Couleur": "Colour",
    "Quantité": "Quantity",
    "Ajouter au panier": "Add to cart",
    "Article épuisé": "Item sold out",
    "Description": "Description",
    "Vous aimerez aussi": "You may also like",
    "Article": "Item",
    # Panier
    "unité": "unit",
    "Retirer": "Remove",
    "Continuer mes achats": "Continue shopping",
    "Récapitulatif": "Summary",
    "Sous-total": "Subtotal",
    "Calculée à la commande": "Calculated at checkout",
    "Total": "Total",
    "Passer commande": "Checkout",
    "Votre panier est vide": "Your cart is empty",
    "Parcourez la boutique et ajoutez vos articles préférés.": "Browse the shop and add your favourite items.",
    "Découvrir la boutique": "Explore the shop",
    "Article retiré du panier.": "Item removed from cart.",
    "Votre panier est vide.": "Your cart is empty.",
    # Checkout
    "Commander": "Checkout",
    "Finaliser ma commande": "Complete my order",
    "Adresse de livraison": "Shipping address",
    "Nom complet": "Full name",
    "E-mail": "Email",
    "Téléphone": "Phone",
    "Adresse": "Address",
    "Ville": "City",
    "Code postal": "Postal code",
    "Pays": "Country",
    "Note (optionnel)": "Note (optional)",
    "Mode de paiement": "Payment method",
    "Carte bancaire": "Credit card",
    "Paiement à la livraison": "Cash on delivery",
    "Paiement 100 % sécurisé. Le paiement par carte est ici en mode démonstration — branchez Stripe ou PayPal pour encaisser réellement.":
        "100% secure payment. Card payment is in demo mode here — connect Stripe or PayPal to charge for real.",
    "Ma commande": "My order",
    "Confirmer la commande": "Confirm order",
    "Retour au panier": "Back to cart",
    # Confirmation
    "Commande confirmée": "Order confirmed",
    "Merci pour votre commande !": "Thank you for your order!",
    "Paiement confirmé (démonstration).": "Payment confirmed (demo).",
    "Vous paierez à la livraison.": "You will pay on delivery.",
    "Voir mes commandes": "View my orders",
    # Compte
    "Bonjour": "Hello",
    "Mot de passe": "Password",
    "Historique des commandes": "Order history",
    "Commande": "Order",
    "Détails": "Details",
    "Aucune commande pour l'instant": "No orders yet",
    "Vos futures commandes apparaîtront ici.": "Your future orders will appear here.",
    "Faire du shopping": "Go shopping",
    "Informations": "Information",
    "Payée": "Paid",
    "Date": "Date",
    "Paiement": "Payment",
    "Qté": "Qty",
    # Statuts
    "En attente": "Pending",
    "Expédiée": "Shipped",
    "Livrée": "Delivered",
    "Annulée": "Cancelled",
    # Auth
    "Ravi de vous revoir chez DressIT": "Welcome back to DressIT",
    "Identifiant ou mot de passe incorrect.": "Incorrect username or password.",
    "Nom d'utilisateur": "Username",
    "Se connecter": "Sign in",
    "Pas encore de compte ?": "No account yet?",
    "Rejoignez DressIT et suivez vos commandes": "Join DressIT and track your orders",
    "Prénom": "First name",
    "Créer mon compte": "Create my account",
    "Déjà inscrit·e ?": "Already registered?",
    "Changer de mot de passe": "Change password",
    "Valider": "Confirm",
    "Retour": "Back",
    "Mot de passe modifié": "Password changed",
    "Votre mot de passe a bien été mis à jour.": "Your password has been updated.",
    "Retour à mon compte": "Back to my account",
    "Bienvenue chez DressIT, votre compte a été créé !": "Welcome to DressIT, your account has been created!",
    # Favoris
    "Mes favoris": "My favourites",
    "Ajouter aux favoris": "Add to favourites",
    "Dans vos favoris": "In your favourites",
    "Retiré de vos favoris.": "Removed from your favourites.",
    "Ajouté à vos favoris ❤️": "Added to your favourites ❤️",
    "Aucun favori pour l'instant": "No favourites yet",
    "Cliquez sur le cœur d'un article pour le retrouver ici.":
        "Click the heart on an item to find it here.",
    # Livraison & promo
    "Offerte": "Free",
    "Remise": "Discount",
    "Code promo": "Promo code",
    "OK": "OK",
    "appliqué": "applied",
    "Code promo retiré.": "Promo code removed.",
    "Code promo invalide.": "Invalid promo code.",
    "Ce code n'est plus actif.": "This code is no longer active.",
    "Ce code a expiré.": "This code has expired.",
    "Ce code a atteint sa limite d'utilisation.": "This code has reached its usage limit.",
    "Livraison offerte": "Free shipping",
    "Paiement sécurisé": "Secure payment",
    "Carte ou à la livraison": "Card or cash on delivery",
    "Retours faciles": "Easy returns",
    "Sous 30 jours": "Within 30 days",
    "Les meilleurs prix": "The best prices",
    "Qualité au juste prix": "Quality at a fair price",
    "Offre de bienvenue": "Welcome offer",
    "Code": "Code",
    "J'en profite": "Shop now",
    # E-mail
    "Récapitulatif :": "Summary:",
    "Livraison à :": "Delivered to:",
    "À bientôt sur DressIT !": "See you soon at DressIT!",
    "À bientôt sur DressIT — la mode aux prix les plus abordables.":
        "See you soon at DressIT — fashion at the most affordable prices.",
    # Langues (menu déroulant Django)
    "Français": "French",
    "English": "English",
}


def build():
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "DressIT 1.0",
        "Report-Msgid-Bugs-To": "",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Language": "en",
    }
    for msgid, msgstr in TRANSLATIONS.items():
        po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

    PO_PATH.parent.mkdir(parents=True, exist_ok=True)
    po.save(str(PO_PATH))
    po.save_as_mofile(str(PO_PATH.with_suffix(".mo")))
    print(f"✔ {len(TRANSLATIONS)} traductions écrites dans {PO_PATH}")
    print(f"✔ Fichier compilé : {PO_PATH.with_suffix('.mo')}")


if __name__ == "__main__":
    build()
