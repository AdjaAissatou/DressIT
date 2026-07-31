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
    # Gestion / tableau de bord
    "Gestion": "Management",
    "Tableau de bord": "Dashboard",
    "Vue d'ensemble de votre boutique DressIT": "Overview of your DressIT store",
    "Nouvel article": "New item",
    "Catégorie": "Category",
    "Studio IA": "AI Studio",
    "Administration": "Admin",
    "Chiffre d'affaires": "Revenue",
    "Commandes": "Orders",
    "Clients": "Customers",
    "comptes créés": "accounts created",
    "Articles": "Items",
    "en vente": "on sale",
    "catégories": "categories",
    "Ruptures de stock": "Out of stock",
    "en stock faible": "low stock",
    "en attente": "pending",
    "Ventes des 14 derniers jours": "Sales over the last 14 days",
    "Statut des commandes": "Order status",
    "Commandes récentes": "Recent orders",
    "Meilleures ventes": "Best sellers",
    "vendus": "sold",
    "Stock à surveiller": "Stock to watch",
    "restants": "left",
    "Tous les stocks sont bons.": "All stock levels are healthy.",
    "Aucune commande pour l'instant.": "No orders yet.",
    "Pas encore de ventes.": "No sales yet.",
    # Studio IA
    "Générer une description": "Generate a description",
    "Générer la description": "Generate description",
    "Nom de l'article": "Item name",
    "Rayon": "Department",
    "Mots-clés, matière, style (optionnel)": "Keywords, material, style (optional)",
    "Enregistrer sur un article (optionnel)": "Save to an item (optional)",
    "Ne pas enregistrer": "Do not save",
    "Créer un visuel (à partir d'un modèle)": "Create a visual (from a template)",
    "Titre affiché": "Displayed title",
    "Sous-titre (optionnel)": "Subtitle (optional)",
    "Type de vêtement": "Garment type",
    "Ambiance (couleur)": "Mood (colour)",
    "Teinte": "Shade",
    "Ajouter aux photos d'un article (optionnel)": "Add to an item's photos (optional)",
    "Aperçu seulement": "Preview only",
    "Générer le visuel": "Generate visual",
    "Télécharger": "Download",
    "Gabarit": "Template",
    "Indiquez au moins le nom de l'article.": "Please provide at least the item name.",
    # Recherche par photo
    "Recherche par photo": "Photo search",
    "Rechercher par photo": "Search by photo",
    "Envoyez la photo d'un vêtement, nous trouvons les articles les plus ressemblants.":
        "Upload a photo of a garment and we'll find the closest matching items.",
    "Choisir une photo": "Choose a photo",
    "JPG ou PNG — un vêtement bien visible fonctionne le mieux.":
        "JPG or PNG — a clearly visible garment works best.",
    "Trouver des articles similaires": "Find similar items",
    "Résultats": "Results",
    "Aucun article ressemblant trouvé": "No similar item found",
    "Essayez une autre photo, plus nette ou plus centrée sur le vêtement.":
        "Try another photo, sharper or more focused on the garment.",
    # Paiement mobile
    "Wave": "Wave",
    "Orange Money": "Orange Money",
    "à configurer": "to configure",
    "Le paiement Wave n'est pas encore configuré.": "Wave payment is not configured yet.",
    "Le paiement Orange Money n'est pas encore configuré.": "Orange Money payment is not configured yet.",
    "Paiement confirmé, merci !": "Payment confirmed, thank you!",
    "Votre paiement est en cours de vérification. Vous recevrez une confirmation.":
        "Your payment is being verified. You will receive a confirmation.",
    "Paiement annulé. Votre commande n'a pas été validée.":
        "Payment cancelled. Your order was not confirmed.",
    "Paiement annulé": "Payment cancelled",
    "Réessayer le paiement": "Retry payment",
    "Paiement confirmé": "Payment confirmed",
    # Aide à la décision
    "Aide à la décision": "Decision support",
    "Panier moyen": "Average order",
    "Meilleurs clients": "Top customers",
    "Total dépensé": "Total spent",
    "Chiffre d'affaires par catégorie": "Revenue by category",
    "Moyens de paiement": "Payment methods",
    "Pas encore de clients.": "No customers yet.",
    # Studio IA (photo modèle)
    "Photo du modèle (optionnel)": "Model photo (optional)",
    "Fournissez une photo : elle sera habillée aux couleurs DressIT. Sinon, une silhouette est générée.":
        "Provide a photo: it will be styled in DressIT colours. Otherwise a silhouette is generated.",
    # Réclamations (SAV)
    "Réclamation": "Complaint",
    "Réclamations": "Complaints",
    "Faire une réclamation": "File a complaint",
    "Un souci avec une commande, une livraison, un article ? Écrivez-nous.":
        "A problem with an order, a delivery, an item? Write to us.",
    "Motif": "Reason",
    "Votre message": "Your message",
    "Commande concernée (optionnel)": "Related order (optional)",
    "Téléphone (optionnel)": "Phone (optional)",
    "Envoyer ma réclamation": "Send my complaint",
    "Mes réclamations": "My complaints",
    "Nouvelle réclamation": "New complaint",
    "Aucune réclamation. Un souci ?": "No complaints. A problem?",
    "Contactez-nous": "Contact us",
    "Réponse": "Reply",
    "Une réclamation ?": "A complaint?",
    "Réclamations récentes": "Recent complaints",
    "Aucune réclamation.": "No complaints.",
    "à traiter": "to handle",
    "Problème de commande": "Order issue",
    "Livraison": "Delivery",
    "Article défectueux": "Faulty item",
    "Remboursement / échange": "Refund / exchange",
    "Autre": "Other",
    "Ouverte": "Open",
    "En cours": "In progress",
    "Résolue": "Resolved",
    "Fermée": "Closed",
    # E-mails
    "Paiement reçu": "Payment received",
    "Votre paiement a bien été reçu": "Your payment has been received",
    "Réponse à votre réclamation": "Reply to your complaint",
    "Nous avons bien reçu votre message": "We have received your message",
    "Votre commande est expédiée": "Your order has shipped",
    "Votre commande est livrée": "Your order has been delivered",
    "La mode à petit prix": "Affordable fashion",
    # IA image
    "Créer un visuel": "Create a visual",
    "IA réelle": "Real AI",
    "Description de l'image (prompt IA)": "Image description (AI prompt)",
    "Génère une vraie image via votre fournisseur d'IA configuré.":
        "Generates a real image via your configured AI provider.",
    # Back-office : réclamations (SAV)
    "réclamation(s)": "complaint(s)",
    "à traiter": "to handle",
    "Nom, e-mail ou n°…": "Name, email or #…",
    "Tous les motifs": "All subjects",
    "Motif": "Subject",
    "Reçue le": "Received",
    "Traiter": "Handle",
    "Aucune réclamation.": "No complaints.",
    "Message du client": "Customer message",
    "Votre réponse": "Your reply",
    "Modifier / renvoyer la réponse": "Edit / resend reply",
    "Répondre au client": "Reply to customer",
    "Message de réponse": "Reply message",
    "Ce texte sera envoyé par e-mail au client.": "This text will be emailed to the customer.",
    "Enregistrer & envoyer": "Save & send",
    "Réponse envoyée à %(e)s.": "Reply sent to %(e)s.",
    "Réclamation mise à jour.": "Complaint updated.",
    # Notifications
    "Notifications": "Notifications",
    "non lue(s)": "unread",
    "Aucune notification": "No notifications",
    "Aucune notification pour le moment.": "No notifications yet.",
    "Vous serez prévenu ici des nouvelles commandes et du suivi.":
        "You'll be notified here of new orders and tracking updates.",
    # Langues (menu déroulant Django)
    "Français": "French",
    "English": "English",
    # Back-office : variantes épuisées
    "épuisé": "sold out",
    "Marquer comme épuisé (affiché mais non commandable)":
        "Mark as sold out (shown but not orderable)",
    "Couleurs épuisées": "Sold-out colors",
    "Tailles épuisées": "Sold-out sizes",
    # Back-office : commandes
    "Détail": "Details",
    "Filtrer": "Filter",
    "Tous les statuts": "All statuses",
    "Tous les rayons": "All departments",
    "Nom, e-mail ou n° de commande…": "Name, email or order #…",
    "commande(s)": "order(s)",
    "Payée": "Paid",
    "Variante": "Variant",
    "Gérer la commande": "Manage order",
    "Marquée comme payée": "Marked as paid",
    "Mettre à jour": "Update",
    "Le client est prévenu par e-mail lors de l'expédition, la livraison ou l'annulation.":
        "The customer is notified by email on shipping, delivery or cancellation.",
    "Compte": "Account",
    "Paiement": "Payment",
    "Qté": "Qty",
    # Back-office : tailles & couleurs
    "Tailles & couleurs": "Sizes & colors",
    "Les variantes proposées lors de la création d'un article.":
        "The variants offered when creating an item.",
    "Ajouter une taille": "Add a size",
    "Ajouter une couleur": "Add a color",
    "Libellé": "Label",
    "Ajouter": "Add",
    "Supprimer cette taille ?": "Delete this size?",
    "Supprimer cette couleur ?": "Delete this color?",
    "Aucune taille.": "No sizes.",
    "Aucune couleur.": "No colors.",
    "Hex": "Hex",
    # Back-office : codes promo
    "Codes promo": "Promo codes",
    "code(s)": "code(s)",
    "Nouveau code": "New code",
    "Min. panier": "Min. cart",
    "Utilisations": "Uses",
    "Validité": "Valid until",
    "Actif": "Active",
    "Inactif": "Inactive",
    "Supprimer ce code ?": "Delete this code?",
    "Aucun code promo.": "No promo codes.",
    "Modifier le code promo": "Edit promo code",
    "Nouveau code promo": "New promo code",
    "Ex : BIENVENUE10. Sera converti en majuscules.":
        "e.g. WELCOME10. Will be uppercased.",
    "Type de remise": "Discount type",
    "Valeur": "Value",
    "10 = -10 % ou -10 FCFA selon le type.": "10 = -10% or -10 FCFA depending on type.",
    "Sous-total minimum": "Minimum subtotal",
    "Utilisations max": "Max uses",
    "Vide = illimité.": "Empty = unlimited.",
    "Valable jusqu'au": "Valid until",
    "Code actif": "Code active",
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
