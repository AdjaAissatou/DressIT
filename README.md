# 👗 DressIT — Plateforme de vente de vêtements

Boutique en ligne **Homme & Femme** construite avec **Django**. Élégante,
multilingue (FR / EN), avec mode **sombre / clair**, thème **marron · beige · doré**
et texte clair.

## ✨ Fonctionnalités

- 🛍️ **Catalogue Homme / Femme / Unisexe** avec catégories, tailles, couleurs et photos
- 🔎 **Recherche, filtres et tri** (prix, nouveautés, nom)
- 🛒 **Panier** (fonctionne sans compte, basé sur la session)
- ❤️ **Liste de favoris (wishlist)** avec bouton cœur instantané
- 🚚 **Frais de livraison** (offerts au-delà d'un montant) et 🎟️ **codes promo**
- 💳 **Commande & paiement** : carte bancaire (mode démonstration) ou paiement à la livraison
- 📧 **E-mail de confirmation** de commande (HTML, aux couleurs de la marque)
- 👤 **Espace client** : inscription, connexion, historique des commandes, changement de mot de passe
- 🎨 **Thème marron/beige/doré**, texte clair, **mode sombre & clair** (mémorisé dans le navigateur)
- 🌍 **Multilingue** : français 🇫🇷 et anglais 🇬🇧, bascule instantanée
- 🖼️ **Gestion des photos** et des articles ultra simple via l'**administration Django**
- 📦 **Gestion des commandes** côté admin (statuts : en attente, payée, expédiée, livrée, annulée)
- ✨ **Images de démonstration générées automatiquement** (en attendant vos vraies photos)

## 🚀 Démarrage rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Préparer la base de données
python manage.py migrate

# 3. (Optionnel) Remplir avec des données de démonstration + compte admin
python manage.py seed_demo --admin
#   → crée un admin : identifiant « admin », mot de passe « admin12345 »
#   ⚠️ à changer immédiatement !

# 4. (Sinon) créer votre propre compte administrateur
python manage.py createsuperuser

# 5. Générer les traductions anglaises (déjà fournies, à relancer après modification)
python compile_translations.py

# 6. Lancer le serveur
python manage.py runserver
```

Ouvrez ensuite :
- **Boutique** : http://127.0.0.1:8000/
- **Administration** : http://127.0.0.1:8000/admin/

## 🧾 Remplir vos articles (sans souci)

Tout se passe dans l'**administration** (`/admin`) :

1. **Tailles** et **Couleurs** : créez-les une fois (déjà pré-remplies par `seed_demo`).
2. **Catégories** : ex. « Robes » (Femme), « Chemises » (Homme)…
3. **Articles** → *Ajouter* :
   - nom, catégorie, rayon (Homme/Femme/Unisexe), description, prix ;
   - *prix barré* optionnel pour afficher une **promotion** ;
   - cochez les tailles et couleurs disponibles ;
   - **glissez vos photos** directement (plusieurs par article) ;
   - « Mis en avant » pour l'afficher sur la page d'accueil.

Les **commandes** des clients arrivent automatiquement dans l'admin, où vous
pouvez changer leur statut et voir le détail.

## 💳 Passer au paiement réel

Le paiement par carte est en **mode démonstration** (la commande est marquée
« payée » sans transaction réelle). Pour encaisser vraiment, intégrez **Stripe**
ou **PayPal** dans `store/views.py` (fonction `checkout`), à l'endroit indiqué
par le commentaire. Ne mettez jamais vos clés secrètes dans le code : utilisez
des **variables d'environnement**.

## 🎨 Personnalisation

- **Couleurs / thème** : `static/css/dressit.css` (variables `--brown-*`, `--gold`, `--beige-*` en haut du fichier).
- **Devise** : variable d'environnement `DRESSIT_CURRENCY_SYMBOL` (par défaut `€`).
- **Traductions** : éditez le dictionnaire dans `compile_translations.py` puis relancez-le.

## ⚙️ Configuration (variables d'environnement)

| Variable | Rôle | Défaut |
|---|---|---|
| `DRESSIT_SECRET_KEY` | Clé secrète Django (obligatoire en prod) | clé de dev |
| `DRESSIT_DEBUG` | `1` = debug activé, `0` = production | `1` |
| `DRESSIT_ALLOWED_HOSTS` | Hôtes autorisés (séparés par `,`) | `*` |
| `DRESSIT_CURRENCY_SYMBOL` | Symbole de devise | `€` |
| `DRESSIT_SHIPPING_FEE` | Frais de livraison | `4.90` |
| `DRESSIT_FREE_SHIPPING_THRESHOLD` | Livraison offerte au-delà de | `50` |
| `DRESSIT_EMAIL_BACKEND` | Backend e-mail (console en dev) | console |
| `DRESSIT_EMAIL_HOST` / `_PORT` / `_HOST_USER` / `_HOST_PASSWORD` | SMTP (prod) | — |
| `DRESSIT_FROM_EMAIL` | Expéditeur des e-mails | `DressIT <no-reply@dressit.local>` |

## 🎟️ Codes promo & 🚚 livraison

- Créez vos **codes promo** dans l'admin (`/admin` → *Codes promo*) : pourcentage
  ou montant fixe, panier minimum, date d'expiration, nombre d'utilisations.
  `seed_demo` en crée trois : `BIENVENUE10` (-10 %), `ETE20` (-20 % dès 40 €),
  `MOINS5` (-5 € dès 25 €).
- La **livraison** est un forfait, **offerte** au-delà du seuil (voir variables
  ci-dessus). Le client voit le total se recalculer en direct dans le panier.

## 📧 E-mails

En développement, les e-mails de confirmation s'affichent dans le terminal
(backend console). Pour les envoyer réellement, renseignez les variables SMTP
`DRESSIT_EMAIL_*` (ex. Gmail, SendGrid, Mailgun…).

## 🗂️ Structure

```
dressit/          → configuration du projet (settings, urls)
store/            → application boutique
  models.py       → Produits, catégories, tailles, couleurs, commandes
  views.py        → Pages, panier, commande, espace client
  admin.py        → Interface d'administration (gestion articles & commandes)
  cart.py         → Panier en session
  forms.py        → Formulaires (inscription, commande)
  management/…    → commande seed_demo
templates/        → gabarits HTML (thème marron/beige/doré)
static/           → CSS et JavaScript (thème, mode sombre/clair)
locale/en/        → traduction anglaise
media/            → photos envoyées (créé à l'usage)
```

---

Fait avec ❤️ pour **DressIT** — la mode aux prix les plus abordables.
