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
- 📊 **Tableau de bord** de gestion : chiffre d'affaires, ventes, meilleures ventes, alertes de stock
- 📥 **Gestion du stock et de la disponibilité** (stock faible / ruptures, activer/désactiver un article)
- 🔎 **Recherche par photo** (client) : moteur de similarité visuelle réel (couleurs + empreinte perceptuelle)
- 💸 **Paiement mobile réel** : **Wave** et **Orange Money** (API officielles, aucune simulation)
- ✨ **Studio IA (super-admin)** : descriptions (Claude) + visuels de marque, **à partir de la photo du modèle**
- 📈 **Aide à la décision** : meilleurs clients, articles les plus vendus, CA par catégorie, panier moyen, moyens de paiement
- 🛎️ **Réclamations (SAV)** : le client dépose une réclamation, l'admin répond (e-mail automatique)
- 📧 **E-mails enrichis** : confirmation de commande, **paiement reçu**, **suivi de statut**, accusés de réclamation
- 🖼️ **Vraies photos de démonstration** (robes, chemises…), plusieurs par article

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

## 📊 Gérer la boutique (tableau de bord & IA)

Un espace de gestion réservé au personnel est disponible sur **`/gestion/`**
(icône 📊 dans l'en-tête une fois connecté en tant qu'admin/staff) :

- **Statistiques** : chiffre d'affaires, commandes, clients, ventes des 14 derniers
  jours, meilleures ventes, répartition des statuts.
- **Stock & disponibilité** : alertes de rupture et de stock faible ; modifiez le
  stock et l'état « en vente » directement dans l'admin (colonnes éditables).
- **Studio IA** (`/gestion/studio-ia/`) :
  - **Descriptions** générées par **Claude** (si `ANTHROPIC_API_KEY` est défini),
    avec repli automatique sur des gabarits hors-ligne.
  - **Visuels de marque** générés à partir d'un modèle (silhouette + dégradé),
    à télécharger ou à attacher directement aux photos d'un article.

Le Studio IA fait partie de **l'espace de gestion** (accessible à tout le
personnel `staff`, pas seulement au super-administrateur Django).

**Descriptions par IA réelle** — activez Claude :
```bash
export ANTHROPIC_API_KEY=sk-ant-...      # + DRESSIT_AI_MODEL (défaut claude-opus-5)
```

**Images IA réelles** (photoréalistes) — branchez un fournisseur d'images
compatible (réponse `b64_json` ou `url`, style API OpenAI Images) :
```bash
export DRESSIT_IMAGE_API_URL=https://api.openai.com/v1/images/generations
export DRESSIT_IMAGE_API_KEY=sk-...
export DRESSIT_IMAGE_MODEL=gpt-image-1     # optionnel
```
Sans fournisseur d'images, le Studio habille la **photo du modèle** que vous
fournissez aux couleurs DressIT, ou génère une silhouette de marque.

### 🛎️ Réclamations (SAV) & e-mails

- Le client dépose une réclamation via `/reclamation/` (lien « Une réclamation ? »
  en pied de page et dans l'espace client). Il reçoit un accusé, et vous êtes
  notifié·e (définissez `DRESSIT_ADMIN_EMAIL`).
- Vous répondez depuis l'admin (`/admin` → *Réclamations*) : saisir la réponse et
  enregistrer **envoie automatiquement l'e-mail au client**.
- **E-mails automatiques** : confirmation de commande, paiement reçu, et **suivi
  de statut** (expédiée / livrée / annulée) — tous aux couleurs de DressIT.

> Ajouter de **nouveaux articles** ou de **nouvelles catégories** se fait dans
> l'admin (`/admin`) — voir la section « Remplir vos articles » ci-dessus.

## 🔎 Recherche par photo

Le client clique sur l'icône 📷 (ou va sur `/recherche-photo/`), envoie la photo
d'un vêtement, et la plateforme classe les articles par ressemblance visuelle
(hash perceptuel + couleurs dominantes, 100 % local, sans service externe).

Les empreintes sont calculées automatiquement à l'ajout d'une photo. Pour
(re)calculer celles d'anciennes photos :

```bash
python manage.py build_signatures        # celles qui manquent
python manage.py build_signatures --all  # tout recalculer
```

## 💸 Paiement mobile : Wave & Orange Money (réel)

Les paiements ne sont **jamais simulés** : la commande n'est marquée « payée »
qu'après confirmation **réelle** de l'opérateur (retour vérifié côté serveur
et/ou webhook signé). Renseignez vos identifiants marchands en variables
d'environnement :

| Variable | Rôle |
|---|---|
| `DRESSIT_SITE_URL` | URL publique HTTPS du site (retours & webhooks) — **obligatoire en prod** |
| `WAVE_API_KEY` | Clé API Wave (`wave_sn_...`) |
| `WAVE_WEBHOOK_SECRET` | Secret de signature des webhooks Wave |
| `OM_MERCHANT_KEY` | Clé marchand Orange Money |
| `OM_CONSUMER_KEY` / `OM_CONSUMER_SECRET` | Identifiants OAuth Orange (ou `OM_AUTH_HEADER`) |
| `OM_ENV` | `dev` (test) ou `prod` |
| `OM_CURRENCY` | Devise Orange (`OUV` en test, `XOF` en prod) |

- **Wave** : `POST https://api.wave.com/v1/checkout/sessions` → redirection vers
  `wave_launch_url`. Webhook signé (HMAC-SHA256) sur `/paiement/wave/webhook/`.
- **Orange Money** : OAuth puis `webpayment` → redirection vers `payment_url`.
  Notification sur `/paiement/orange/webhook/`.

Sans identifiants, l'option est visible mais refuse de valider (message clair,
aucune commande fantôme). Le **paiement à la livraison** fonctionne sans clé.

> Docs : [Wave Checkout](https://docs.wave.com/checkout) ·
> [Orange Money Web Payment](https://developer.orange.com/apis/om-webpay).
> Les paramètres exacts (devise, endpoints dev/prod) dépendent de votre contrat
> marchand — vérifiez-les auprès de l'opérateur.

## 📱 API REST & application mobile

Une **API REST** (Django REST Framework) alimente l'**application mobile**
(dossier [`mobile/`](mobile/), Expo / React Native).

**Endpoints principaux** (préfixe `/api/`, jeton d'authentification) :

| Méthode | Endpoint | Rôle |
|---|---|---|
| POST | `/api/auth/register/` · `/api/auth/login/` | Inscription / connexion (retourne un jeton) |
| GET | `/api/auth/me/` | Profil connecté |
| GET | `/api/config/` | Devise, livraison, passerelles actives |
| GET | `/api/categories/` · `/api/products/` | Catalogue (filtres `gender`, `category`, `q`, `sort`) |
| GET | `/api/products/<slug>/` | Fiche article |
| POST | `/api/products/search-photo/` | Recherche par photo (multipart) |
| GET/POST | `/api/wishlist/` | Favoris (liste / bascule) |
| POST | `/api/promo/validate/` | Valider un code promo |
| POST | `/api/orders/create/` | Créer une commande (+ URL de paiement Wave/OM) |
| GET | `/api/orders/` · `/api/orders/<id>/` | Mes commandes |
| GET/POST | `/api/complaints/` | Réclamations |

**Lancer l'app mobile** (téléphone via Expo Go) :
```bash
python manage.py runserver 0.0.0.0:8000     # backend accessible sur le réseau
cd mobile && npm install && npm start        # puis scannez le QR code
```
Réglez l'URL de l'API (IP de votre machine) dans `mobile/app.json` → `extra.apiUrl`.
Détails dans [`mobile/README.md`](mobile/README.md).

## 💳 Passer au paiement carte (optionnel)

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
