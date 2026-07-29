"""Recherche par photo : moteur de similarité visuelle (réel, hors-ligne).

Chaque photo d'article possède une « empreinte » calculée avec Pillow :
 - un hash perceptuel 8×8 (structure de l'image) ;
 - une grille de couleurs 4×4 (couleurs dominantes).

La recherche compare l'empreinte de la photo envoyée par le client à celles des
articles et classe par distance croissante. Aucun service externe n'est requis.
"""

import json
import math

from PIL import Image

HASH_SIZE = 8          # 8×8 = 64 bits
COLOR_GRID = 4         # grille 4×4 → 48 valeurs (RGB)
MAX_RESULTS = 24
# En-dessous de ce seuil de distance, on considère l'article « ressemblant ».
MATCH_THRESHOLD = 0.55


def compute_signature(image_file):
    """Calcule l'empreinte d'une image. Accepte un chemin ou un fichier binaire.

    Retourne une chaîne JSON, ou "" en cas d'échec.
    """
    try:
        img = Image.open(image_file).convert("RGB")
    except Exception:
        return ""

    # --- hash perceptuel (aHash) ---
    small = img.resize((HASH_SIZE, HASH_SIZE)).convert("L")
    pixels = list(small.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for i, p in enumerate(pixels):
        if p >= avg:
            bits |= 1 << i

    # --- grille de couleurs dominantes ---
    grid = img.resize((COLOR_GRID, COLOR_GRID))
    colors = []
    for px in grid.getdata():
        colors.extend(px[:3])

    return json.dumps({"h": str(bits), "c": colors})


def _parse(sig):
    try:
        data = json.loads(sig)
        return int(data["h"]), data["c"]
    except (ValueError, KeyError, TypeError):
        return None


def _distance(a, b):
    """Distance normalisée [0..1] entre deux empreintes (0 = identiques)."""
    ha, ca = a
    hb, cb = b
    # Hamming sur le hash 64 bits.
    hamming = bin(ha ^ hb).count("1")
    hash_norm = hamming / (HASH_SIZE * HASH_SIZE)
    # Euclidienne sur les couleurs.
    ssum = sum((x - y) ** 2 for x, y in zip(ca, cb))
    color_norm = math.sqrt(ssum) / (255 * math.sqrt(len(ca)))
    return 0.45 * hash_norm + 0.55 * color_norm


def search(query_file, limit=MAX_RESULTS):
    """Retourne une liste de (product, distance) triée du plus ressemblant au moins.

    Import local des modèles pour éviter les imports circulaires.
    """
    from .models import ProductImage

    q = _parse(compute_signature(query_file))
    if q is None:
        return []

    best = {}  # product_id -> (product, distance)
    qs = ProductImage.objects.exclude(signature="").select_related("product")
    for img in qs:
        product = img.product
        if not product or not product.is_active:
            continue
        parsed = _parse(img.signature)
        if parsed is None:
            continue
        d = _distance(q, parsed)
        if product.id not in best or d < best[product.id][1]:
            best[product.id] = (product, d)

    ranked = sorted(best.values(), key=lambda t: t[1])
    return ranked[:limit]
