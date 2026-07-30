# 📱 DressIT Mobile (Expo / React Native)

Application mobile de la boutique DressIT, connectée à l'**API REST** du backend
Django (`/api/`). Elle tourne sur votre téléphone (Android/iOS) via **Expo Go**,
sans compilation.

## Fonctionnalités
- 🛍️ Catalogue Homme/Femme avec recherche et filtres
- 👗 Fiche article (photos, tailles, couleurs) + ajout au panier
- 📷 **Recherche par photo** (caméra ou galerie)
- 🛒 Panier persistant + commande
- 💸 Paiement **Wave / Orange Money** (ouverture de la page opérateur) ou à la livraison
- 👤 Inscription / connexion (jeton) + historique des commandes

## Prérequis
- [Node.js 18+](https://nodejs.org)
- L'application **Expo Go** sur votre téléphone ([Android](https://play.google.com/store/apps/details?id=host.exp.exponent) / [iOS](https://apps.apple.com/app/expo-go/id982107779))
- Le **backend Django lancé** et accessible depuis le téléphone (même réseau Wi-Fi)

## Configuration de l'URL de l'API
Le téléphone ne peut pas joindre `localhost` : utilisez l'**IP de votre machine**
sur le réseau local. Trouvez-la (`ipconfig` sous Windows, `ifconfig`/`ip a` sous
macOS/Linux), puis éditez `app.json` :

```json
"extra": { "apiUrl": "http://192.168.1.10:8000/api" }
```

Et lancez le backend en écoutant sur toutes les interfaces :
```bash
python manage.py runserver 0.0.0.0:8000
```
(Ajoutez votre IP à `DRESSIT_ALLOWED_HOSTS` si besoin ; le CORS est déjà ouvert en dev.)

## Lancer l'app
```bash
cd mobile
npm install
npm start          # affiche un QR code
```
Scannez le QR code avec **Expo Go** (Android) ou l'appareil photo (iOS).

## Structure
```
App.js                 navigation (onglets + pile)
src/api.js             client HTTP (jeton auto)
src/store.js           contextes auth + panier (persistés)
src/theme.js           couleurs DressIT
src/components/        ProductCard
src/screens/           Boutique, Article, Recherche photo, Panier, Commande, Compte
```

## Passer en production
- Hébergez le backend (HTTPS public) et mettez son URL dans `app.json` > `extra.apiUrl`.
- Construisez les binaires avec **EAS Build** (`npx eas build -p android`).
