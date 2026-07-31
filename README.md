# 👗 DressIT — Plateforme de vente de vêtements

Boutique en ligne **Homme & Femme** construite avec **Django**. Élégante,
multilingue (FR / EN), avec mode **sombre / clair**, thème **marron · beige · doré**
et texte clair. Prix en **FCFA**, paiements **Wave** et **Orange Money** réels.

## ✨ Fonctionnalités

**Boutique (côté client)**
- 🛍️ **Catalogue Homme / Femme / Unisexe** avec catégories, tailles, couleurs et photos
- 🔎 **Recherche, filtres et tri** (prix, nouveautés, nom)
- 📷 **Recherche par photo** : moteur de similarité visuelle réel (couleurs + empreinte perceptuelle, 100 % local)
- 🛒 **Panier** (basé sur la session) · ❤️ **Favoris** avec bouton cœur instantané
- 🚚 **Frais de livraison** (offerts au-delà d'un seuil) et 🎟️ **codes promo**
- ⛔ **Variantes épuisées** : une couleur / taille précise peut être grisée et non commandable ; un article en rupture apparaît grisé
- 💸 **Paiement mobile réel** : **Wave** et **Orange Money** (API officielles, **aucune simulation**) ou **paiement à la livraison**
- 🔒 **Commande réservée aux comptes** (connexion obligatoire au moment de payer)
- 👤 **Espace client** : inscription, connexion, historique des commandes, favoris, réclamations
- 🔔 **Notifications** in-app (cloche) + e-mails, **en temps réel**
- 🌍 **Multilingue** FR 🇫🇷 / EN 🇬🇧 et 🎨 **thème sombre / clair** (mémorisé dans le navigateur)

**Back-office (côté gérant·e)** — un espace `/gestion/` au **même thème que la boutique**, hors admin Django :
- 📊 **Tableau de bord** : chiffre d'affaires, ventes des 14 derniers jours, meilleures ventes, statuts, **aide à la décision** (meilleurs clients, CA par catégorie, panier moyen, moyens de paiement)
- 👗 **Articles** : création / édition avec photos multiples, tailles, couleurs, variantes épuisées, stock, mise en avant
- 🗂️ **Catégories** · 🎨 **Tailles & couleurs** · 🎟️ **Codes promo** : tout se gère depuis le back-office
- 🧾 **Commandes** : liste filtrable, détail, changement de statut (e-mail client automatique)
- 🛎️ **Réclamations (SAV)** : traitez et répondez au client (e-mail automatique)
- ✨ **Studio IA** : descriptions (Claude) + visuels de marque à partir de la photo du modèle
- 📥 **Stock & disponibilité** : alertes de rupture / stock faible

**Technique**
- 📧 **E-mails enrichis** (HTML aux couleurs de la marque) : confirmation, paiement reçu, suivi de statut, SAV, **+ notification admin à chaque commande**
- 📱 **API REST** (Django REST Framework) + **application mobile** Expo / React Native
- 🖼️ **Vraies photos de démonstration**, plusieurs par article

## 🚀 Démarrage rapide

```bash
# 1. Installer les dépendances (utilisez « python -m pip » pour être sûr du bon Python)
python -m pip install -r requirements.txt

# 2. Configurer les clés (facultatif mais recommandé) — voir docs/GENERER_LES_CLES.md
copy .env.example .env        # Windows   (Linux/macOS : cp .env.example .env)

# 3. Préparer la base de données
python manage.py migrate

# 4. (Optionnel) Données de démonstration + compte admin
python manage.py seed_demo --admin
#   → admin : identifiant « admin », mot de passe « admin12345 »  (à changer !)

# 5. (Sinon) créer votre propre compte administrateur
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

Ouvrez ensuite :
- **Boutique** : http://127.0.0.1:8000/
- **Back-office (gestion)** : http://127.0.0.1:8000/gestion/  *(connecté avec un compte staff — icône 📊 dans l'en-tête)*
- **Admin Django** (secours) : http://127.0.0.1:8000/admin/

> 💡 **Windows — erreur `No module named 'rest_framework'` ?** C'est que `pip` et
> `python` ne pointent pas au même interpréteur. Utilisez `python -m pip install
> -r requirements.txt`, ou travaillez dans un environnement virtuel (`python -m
> venv venv` puis `venv\Scripts\activate`).

## 🔑 Clés & configuration (`.env`)

Toutes les clés se rangent dans un fichier **`.env`** à la racine (chargé
automatiquement, pratique sous Windows). Copiez le modèle documenté
[`.env.example`](.env.example) puis complétez.

👉 **Guide pas-à-pas complet : [`docs/GENERER_LES_CLES.md`](docs/GENERER_LES_CLES.md)**
(comment générer la `SECRET_KEY` Django et où obtenir les clés Wave, Orange
Money et Anthropic).

| Variable | Rôle | Défaut |
|---|---|---|
| `DRESSIT_SECRET_KEY` | Clé secrète Django (obligatoire en prod) | clé de dev |
| `DRESSIT_DEBUG` | `1` = debug, `0` = production | `1` |
| `DRESSIT_ALLOWED_HOSTS` | Hôtes autorisés (séparés par `,`) | `*` |
| `DRESSIT_SITE_URL` | URL publique HTTPS (retours & webhooks de paiement) | — |
| `DRESSIT_CURRENCY_SYMBOL` | Symbole de devise | `FCFA` |
| `DRESSIT_SHIPPING_FEE` | Frais de livraison | `2000` |
| `DRESSIT_FREE_SHIPPING_THRESHOLD` | Livraison offerte au-delà de | `30000` |
| `WAVE_API_KEY` · `WAVE_WEBHOOK_SECRET` | Paiement Wave | — |
| `OM_MERCHANT_KEY` · `OM_CONSUMER_KEY` · `OM_CONSUMER_SECRET` · `OM_ENV` | Paiement Orange Money | — |
| `ANTHROPIC_API_KEY` | Studio IA (descriptions par Claude) | — |
| `DRESSIT_IMAGE_API_URL` · `DRESSIT_IMAGE_API_KEY` | Fournisseur d'images IA (facultatif) | — |
| `DRESSIT_ADMIN_EMAIL` | Adresse qui reçoit les notifications (nouvelles commandes, SAV) | — |
| `DRESSIT_EMAIL_BACKEND` + `DRESSIT_EMAIL_HOST` / `_PORT` / `_HOST_USER` / `_HOST_PASSWORD` | SMTP (prod) | console |
| `DRESSIT_FROM_EMAIL` | Expéditeur des e-mails | `DressIT <no-reply@dressit.local>` |
| `DRESSIT_CORS_ORIGINS` | Domaines autorisés pour l'API mobile | — |

## 📊 Gérer la boutique (back-office `/gestion/`)

Tout se gère dans un espace au **même thème que la boutique**, réservé au
personnel (`is_staff`). Le menu du haut donne accès à :

| Page | URL | Rôle |
|---|---|---|
| 📊 Tableau de bord | `/gestion/` | Statistiques, aide à la décision, alertes de stock |
| 👗 Articles | `/gestion/articles/` | Créer / éditer un article, photos, variantes, stock |
| 🗂️ Catégories | `/gestion/categories/` | Gérer les catégories |
| 🧾 Commandes | `/gestion/commandes/` | Liste filtrable + détail + changement de statut |
| 🎨 Tailles & couleurs | `/gestion/variantes/` | Ajouter / supprimer tailles et couleurs |
| 🎟️ Codes promo | `/gestion/codes-promo/` | Créer / éditer / supprimer les codes promo |
| 🛎️ Réclamations | `/gestion/reclamations/` | Traiter le SAV et répondre au client |
| ✨ Studio IA | `/gestion/studio-ia/` | Descriptions (Claude) + visuels de marque |

> Les **filtres** (statut, rayon, motif…) s'appliquent dès que vous changez la
> liste déroulante — pas besoin de bouton.

### 🧾 Remplir vos articles (sans souci)

Dans **Gestion → Articles → Nouvel article** :
- nom, catégorie, rayon (Homme / Femme / Unisexe), description, prix ;
- *prix barré* optionnel pour afficher une **promotion** ;
- cochez les **tailles** et **couleurs** disponibles ;
- marquez une couleur / taille comme **épuisée** (affichée mais non commandable) ;
- **glissez vos photos** (plusieurs par article) ;
- « Mis en avant » pour l'afficher sur la page d'accueil.

> Astuce : générez la description avec le **Studio IA**, puis attachez-la à
> l'article.

## 🔔 Notifications (admin & client)

Vous ne ratez plus rien : notifications **in-app (cloche 🔔)** + **e-mails**, avec
mise à jour **en temps réel** (la cloche s'actualise seule toutes les 20 s, avec
un toast à l'arrivée d'une nouvelle notification — sans WebSocket ni Redis).

| Événement | Admin | Client |
|---|:---:|:---:|
| 🧾 Nouvelle commande | 🔔 + e-mail | 🔔 (+ e-mail de confirmation) |
| 💰 Paiement reçu | 🔔 | 🔔 + e-mail |
| 🚚 Changement de statut | — | 🔔 + e-mail (expédiée / livrée / annulée) |
| 🛎️ Nouvelle réclamation / réponse SAV | 🔔 + e-mail | 🔔 + e-mail |

Renseignez `DRESSIT_ADMIN_EMAIL` (et le SMTP en prod) pour recevoir les e-mails.
La **cloche in-app fonctionne sans aucune configuration**.

## 💸 Paiement mobile : Wave & Orange Money (réel)

Les paiements ne sont **jamais simulés** : la commande n'est marquée « payée »
qu'après confirmation **réelle** de l'opérateur (retour vérifié côté serveur
et/ou webhook signé).

- **Wave** : `POST https://api.wave.com/v1/checkout/sessions` → redirection vers
  `wave_launch_url`. Webhook signé (HMAC-SHA256) sur `/paiement/wave/webhook/`.
- **Orange Money** : OAuth puis `webpayment` → redirection vers `payment_url`.
  Notification sur `/paiement/orange/webhook/`.

Sans identifiants, le moyen de paiement **n'est pas proposé** (aucune commande
fantôme). Le **paiement à la livraison** fonctionne sans clé.

Vérifier que les passerelles sont bien configurées :
```bash
python manage.py shell -c "from store import payments as p; print('Wave:', p.wave_enabled(), '| Orange:', p.om_enabled())"
```

> Le webhook exige une URL publique HTTPS. En test local, utilisez un tunnel
> (`ngrok http 8000`) et renseignez `DRESSIT_SITE_URL`.
> Docs : [Wave Checkout](https://docs.wave.com/checkout) ·
> [Orange Money Web Payment](https://developer.orange.com/apis/om-webpay).

## ✨ Studio IA

Dans **Gestion → Studio IA** :
- **Descriptions** générées par **Claude** si `ANTHROPIC_API_KEY` est défini
  (repli automatique sur des gabarits hors-ligne sinon) ;
- **Visuels de marque** générés à partir de la photo d'un modèle (habillée aux
  couleurs DressIT) ou d'une silhouette générée ; option **vraie image IA** en
  branchant un fournisseur compatible (`DRESSIT_IMAGE_API_URL` / `_KEY`).

## 📷 Recherche par photo

Le client clique sur 📷 (ou `/recherche-photo/`), envoie la photo d'un vêtement,
et la plateforme classe les articles par ressemblance visuelle (hash perceptuel
+ couleurs dominantes, 100 % local). Les empreintes sont calculées à l'ajout
d'une photo ; pour (re)calculer d'anciennes photos :

```bash
python manage.py build_signatures        # celles qui manquent
python manage.py build_signatures --all  # tout recalculer
```

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

Un aperçu des écrans peut être régénéré avec `python scripts/mobile_preview.py`.

## 🎟️ Codes promo & 🚚 livraison

- Créez vos **codes promo** dans **Gestion → Codes promo** : pourcentage ou
  montant fixe, panier minimum, date d'expiration, nombre d'utilisations.
  `seed_demo` en crée trois : `BIENVENUE10` (-10 %), `ETE20` (-20 % dès 25 000 FCFA),
  `MOINS2000` (-2 000 FCFA dès 15 000 FCFA).
- La **livraison** est un forfait, **offerte** au-delà du seuil (voir variables).
  Le total se recalcule en direct dans le panier.

## 📧 E-mails

En développement, les e-mails s'affichent dans le **terminal** (backend console).
Pour les envoyer réellement, renseignez les variables SMTP `DRESSIT_EMAIL_*`
(ex. Gmail, SendGrid, Mailgun…) et `DRESSIT_ADMIN_EMAIL`.

## 🌍 Traductions

Les traductions anglaises sont fournies. Après avoir modifié le dictionnaire
dans `compile_translations.py` :
```bash
python compile_translations.py     # régénère locale/en/LC_MESSAGES/django.(po|mo)
```
*(N'utilise pas `msgfmt` : le script écrit directement les fichiers `.po` et `.mo`
via `polib`.)*

## 🎨 Personnalisation

- **Couleurs / thème** : `static/css/dressit.css` (variables `--brown-*`, `--gold`, `--beige-*` en haut du fichier).
- **Devise / livraison** : variables `DRESSIT_CURRENCY_SYMBOL`, `DRESSIT_SHIPPING_FEE`, `DRESSIT_FREE_SHIPPING_THRESHOLD`.

## 🗂️ Structure

```
dressit/            → configuration du projet (settings, urls, .env)
store/              → application boutique
  models.py         → Produits, catégories, tailles, couleurs, commandes,
                      codes promo, réclamations, favoris, notifications
  views.py          → Pages, panier, commande, espace client, notifications
  staff.py          → Back-office (tableau de bord, articles, commandes, SAV…)
  payments.py       → Intégrations réelles Wave & Orange Money
  notifications.py  → Notifications in-app (admin & client)
  emails.py         → E-mails transactionnels (HTML + texte)
  signals.py        → E-mails / notifications automatiques (statuts de commande)
  imagesearch.py    → Recherche par photo (empreinte perceptuelle)
  ai.py             → Studio IA (Claude + images)
  cart.py · wishlist.py · forms.py · context_processors.py
  api/              → API REST (DRF) pour l'app mobile
  management/…      → commandes seed_demo, build_signatures
templates/          → gabarits HTML (thème marron/beige/doré)
  store/manage/     → pages du back-office
  emails/           → gabarits d'e-mails
static/             → CSS et JavaScript (thème, cloche temps réel…)
locale/en/          → traduction anglaise
mobile/             → application Expo / React Native
docs/               → guides (GENERER_LES_CLES.md)
media/              → photos envoyées (créé à l'usage)
```

---

Fait avec ❤️ pour **DressIT** — la mode aux prix les plus abordables.
