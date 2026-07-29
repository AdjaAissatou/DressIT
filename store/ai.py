"""Assistant IA de la boutique.

- Génération de descriptions d'articles avec l'API Claude (SDK Anthropic).
- Repli hors-ligne : un générateur par gabarit si la clé API est absente ou
  si l'appel échoue, pour que le Studio IA fonctionne toujours.

Configuration (variables d'environnement) :
  ANTHROPIC_API_KEY   clé API Claude (https://console.anthropic.com)
  DRESSIT_AI_MODEL    modèle à utiliser (défaut : claude-opus-5)
"""

import os
import random

from django.conf import settings

DEFAULT_MODEL = os.environ.get("DRESSIT_AI_MODEL", "claude-opus-5")


def ai_available():
    """Vrai si une clé API Claude est configurée."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


SYSTEM_PROMPT = (
    "Tu es le rédacteur produit de DressIT, une boutique de mode Homme & Femme "
    "aux prix abordables. Tu écris des descriptions d'articles élégantes, "
    "concises et vendeuses, en français, sans emojis. 2 à 3 phrases maximum, "
    "ton chaleureux et haut de gamme. Réponds uniquement par la description, "
    "sans introduction ni guillemets."
)


def generate_description(name, category="", gender="", keywords="", currency=None):
    """Retourne (texte, source) où source ∈ {"claude", "gabarit"}."""
    if ai_available():
        try:
            return _generate_with_claude(name, category, gender, keywords), "claude"
        except Exception:  # pragma: no cover - dépend du réseau / de la clé
            pass
    return _generate_fallback(name, category, gender, keywords), "gabarit"


def _generate_with_claude(name, category, gender, keywords):
    import anthropic

    client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement
    details = []
    if category:
        details.append(f"Catégorie : {category}")
    if gender:
        details.append(f"Rayon : {gender}")
    if keywords:
        details.append(f"Mots-clés / matière / style : {keywords}")
    detail_text = "\n".join(details)

    prompt = (
        f"Rédige la description de vente de l'article suivant.\n"
        f"Nom : {name}\n{detail_text}"
    )
    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [block.text for block in message.content if block.type == "text"]
    return "".join(parts).strip()


# --------------------------------------------------------------------------- #
# Repli hors-ligne : compose une description crédible à partir de fragments.
# --------------------------------------------------------------------------- #
_INTROS = [
    "Découvrez {name}, une pièce {adj} qui sublime votre garde-robe.",
    "{name} : l'alliance parfaite du style et du confort.",
    "Craquez pour {name}, un incontournable {adj} de la saison.",
    "Adoptez {name}, une création {adj} pensée pour vous accompagner partout.",
]
_MIDDLES = [
    "Sa coupe soignée et ses finitions élégantes en font un allié du quotidien comme des grandes occasions.",
    "Confectionné avec soin, il se porte aussi bien au bureau qu'en week-end.",
    "Ses matières douces et sa silhouette flatteuse conviennent à toutes les morphologies.",
    "Facile à assortir, il se glisse dans toutes vos tenues avec une élégance naturelle.",
]
_OUTROS = [
    "Le tout à un prix DressIT, toujours plus doux.",
    "Qualité et petit prix, la promesse DressIT.",
    "Un raffinement accessible, comme on les aime.",
    "L'élégance à petit prix, signée DressIT.",
]
_ADJS = ["raffinée", "élégante", "tendance", "intemporelle", "chic", "moderne"]


def _generate_fallback(name, category, gender, keywords):
    adj = random.choice(_ADJS)
    intro = random.choice(_INTROS).format(name=name, adj=adj)
    middle = random.choice(_MIDDLES)
    if keywords:
        middle = f"{middle} Points forts : {keywords}."
    outro = random.choice(_OUTROS)
    return f"{intro} {middle} {outro}"
