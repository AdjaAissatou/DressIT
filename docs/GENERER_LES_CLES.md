# 🔑 Générer / obtenir les clés de DressIT

Toutes les clés se rangent dans un fichier **`.env`** à la racine du projet.
Copiez d'abord le modèle :

```bash
# Linux / macOS
cp .env.example .env
# Windows
copy .env.example .env
```

Puis remplissez les valeurs ci-dessous. Le fichier `.env` n'est **jamais**
versionné (il est dans `.gitignore`) : vos secrets restent chez vous.

> ⚠️ Règle d'or : ne collez jamais une vraie clé dans `.env.example` ni dans un
> commit. Uniquement dans `.env`.

---

## 1. `DRESSIT_SECRET_KEY` — clé Django (à générer soi-même)

C'est la seule clé qui se **génère** localement. Elle sécurise les sessions et
les cookies.

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Copiez la ligne affichée dans `.env` :

```
DRESSIT_SECRET_KEY=colle-la-cle-generee-ici
```

En production, générez-en une **nouvelle** et gardez-la secrète.

---

## 2. Wave — `WAVE_API_KEY` + `WAVE_WEBHOOK_SECRET`

Wave délivre la clé après validation de votre compte marchand ; elle ne se
génère pas par code.

1. Créez un compte **Wave Business** : https://business.wave.com
   (ou l'application *Wave Business*). Un compte pro est requis.
2. Portail marchand → section **Développeurs / API**.
3. **Générer une clé API** → vous obtenez une clé `wave_sn_...` → `WAVE_API_KEY`.
4. Ajoutez un **Webhook** :
   - URL : `https://VOTRE-DOMAINE/paiement/wave/webhook/`
   - Wave affiche un **secret de webhook** → `WAVE_WEBHOOK_SECRET`.
5. Dans `.env` :
   ```
   WAVE_API_KEY=wave_sn_xxxxxxxxxxxxxxxx
   WAVE_WEBHOOK_SECRET=le-secret-affiche-par-wave
   ```

> 💡 Le webhook exige une URL publique HTTPS. En local, utilisez un tunnel :
> `ngrok http 8000`, puis l'URL `https://xxxx.ngrok.io/paiement/wave/webhook/`.

Dès que `WAVE_API_KEY` est renseignée, le paiement Wave apparaît automatiquement
au moment de la commande (sans clé : rien n'est proposé, aucune simulation).

---

## 3. Orange Money — `OM_MERCHANT_KEY`, `OM_CONSUMER_KEY`, `OM_CONSUMER_SECRET`

1. Créez un compte : https://developer.orange.com
2. Catalogue d'API → **Orange Money Web Payment** → **Souscrire**.
3. Créez une **application** : Orange fournit un **Client ID**
   (`OM_CONSUMER_KEY`) et un **Client Secret** (`OM_CONSUMER_SECRET`).
   - Variante : Orange fournit parfois un en-tête tout prêt
     `Authorization: Basic xxxx`. Dans ce cas, mettez-le dans `OM_AUTH_HEADER`
     et laissez `OM_CONSUMER_KEY` / `OM_CONSUMER_SECRET` vides.
4. La **clé marchand** `OM_MERCHANT_KEY` est fournie par **Orange Money** lors de
   l'activation de votre contrat marchand Web Payment.
5. Dans `.env` :
   ```
   OM_MERCHANT_KEY=votre-cle-marchand
   OM_CONSUMER_KEY=votre-client-id
   OM_CONSUMER_SECRET=votre-client-secret
   OM_ENV=dev          # dev = test Orange ; prod = production
   ```

L'URL de notification à déclarer chez Orange, si demandée :
`https://VOTRE-DOMAINE/paiement/orange/webhook/`.

---

## 4. (Facultatif) `ANTHROPIC_API_KEY` — Studio IA (descriptions par Claude)

1. https://console.anthropic.com → connexion.
2. **Settings → API Keys → Create Key**.
3. Copiez la clé (`sk-ant-...`) dans `.env` :
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxx
   ```

Sans cette clé, le Studio IA reste utilisable (visuels de marque générés
localement), mais les descriptions ne sont pas rédigées par Claude.

---

## 5. Vérifier que tout est bien pris en compte

Redémarrez le serveur après chaque modification de `.env`, puis :

```bash
python manage.py shell -c "from store import payments as p; print('Wave:', p.wave_enabled(), '| Orange:', p.om_enabled())"
```

- `Wave: True` / `Orange: True` → la passerelle est active et proposée au client.
- `False` → la clé correspondante manque encore (aucun paiement simulé).

---

## Récapitulatif du fichier `.env`

| Variable | Source | Obligatoire ? |
|----------|--------|---------------|
| `DRESSIT_SECRET_KEY` | générée localement (commande) | ✅ oui |
| `WAVE_API_KEY` | portail Wave Business | pour activer Wave |
| `WAVE_WEBHOOK_SECRET` | Wave (config webhook) | pour valider les paiements Wave |
| `OM_MERCHANT_KEY` | Orange Money (contrat marchand) | pour activer Orange Money |
| `OM_CONSUMER_KEY` / `OM_CONSUMER_SECRET` | portail développeur Orange | pour activer Orange Money |
| `ANTHROPIC_API_KEY` | console.anthropic.com | facultatif (Studio IA) |
| E-mails SMTP | votre hébergeur / fournisseur | facultatif (prod) |
