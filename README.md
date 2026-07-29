# 👗 DressIT — Plateforme de vente de vêtements

Boutique en ligne **Homme & Femme** construite avec **Django**. Élégante,
multilingue (FR / EN), avec mode **sombre / clair**, thème **marron · beige · doré**
et texte clair.

## ✨ Fonctionnalités

- 🛍️ **Catalogue Homme / Femme / Unisexe** avec catégories, tailles, couleurs et photos
- 🔎 **Recherche, filtres et tri** (prix, nouveautés, nom)
- 🛒 **Panier** (fonctionne sans compte, basé sur la session)
- 💳 **Commande & paiement** : carte bancaire (mode démonstration) ou paiement à la livraison
- 👤 **Espace client** : inscription, connexion, historique des commandes, changement de mot de passe
- 🎨 **Thème marron/beige/doré**, texte clair, **mode sombre & clair** (mémorisé dans le navigateur)
- 🌍 **Multilingue** : français 🇫🇷 et anglais 🇬🇧, bascule instantanée
- 🖼️ **Gestion des photos** et des articles ultra simple via l'**administration Django**
- 📦 **Gestion des commandes** côté admin (statuts : en attente, payée, expédiée, livrée, annulée)

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
