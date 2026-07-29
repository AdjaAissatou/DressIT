"""Génère des images de démonstration élégantes (dégradé + silhouette de vêtement).

Utilisé par la commande `seed_demo` pour que la boutique soit visuellement
attrayante immédiatement, en attendant vos vraies photos.
"""

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 800, 1000

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Paires de dégradé (haut, bas) dans les tons marron/beige/doré.
PALETTES = [
    ((59, 42, 34), (107, 79, 58)),
    ((85, 64, 47), (138, 106, 69)),
    ((74, 53, 36), (166, 124, 46)),
    ((107, 79, 58), (201, 162, 75)),
    ((92, 68, 51), (179, 129, 61)),
    ((67, 47, 34), (122, 90, 58)),
]

GARMENT_FILL = (232, 221, 201, 235)
GARMENT_OUTLINE = (244, 236, 221, 255)


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:  # pragma: no cover
        return ImageFont.load_default()


def _gradient(top, bottom):
    base = Image.new("RGB", (WIDTH, HEIGHT), top)
    top_r, top_g, top_b = top
    bot_r, bot_g, bot_b = bottom
    draw = ImageDraw.Draw(base)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return base


def _poly(points):
    """Convertit des points normalisés (0..1) en pixels centrés."""
    return [(x * WIDTH, y * HEIGHT) for x, y in points]


# Silhouettes normalisées (x: 0..1 largeur, y: 0..1 hauteur).
GARMENTS = {
    "tshirt": [
        (0.30, 0.28), (0.22, 0.34), (0.15, 0.44), (0.24, 0.50), (0.30, 0.45),
        (0.30, 0.74), (0.70, 0.74), (0.70, 0.45), (0.76, 0.50), (0.85, 0.44),
        (0.78, 0.34), (0.70, 0.28), (0.60, 0.30), (0.50, 0.34), (0.40, 0.30),
    ],
    "shirt": [
        (0.32, 0.27), (0.22, 0.33), (0.14, 0.45), (0.23, 0.52), (0.31, 0.46),
        (0.31, 0.78), (0.69, 0.78), (0.69, 0.46), (0.77, 0.52), (0.86, 0.45),
        (0.78, 0.33), (0.68, 0.27), (0.58, 0.29), (0.50, 0.40), (0.42, 0.29),
    ],
    "dress": [
        (0.34, 0.26), (0.26, 0.32), (0.19, 0.42), (0.27, 0.48), (0.36, 0.43),
        (0.36, 0.52), (0.20, 0.82), (0.30, 0.86), (0.50, 0.83), (0.70, 0.86),
        (0.80, 0.82), (0.64, 0.52), (0.64, 0.43), (0.73, 0.48), (0.81, 0.42),
        (0.74, 0.32), (0.66, 0.26), (0.50, 0.30),
    ],
    "skirt": [
        (0.36, 0.40), (0.64, 0.40), (0.66, 0.44), (0.80, 0.78), (0.70, 0.82),
        (0.50, 0.79), (0.30, 0.82), (0.20, 0.78), (0.34, 0.44),
    ],
    "pants": [
        (0.36, 0.34), (0.64, 0.34), (0.66, 0.55), (0.62, 0.80), (0.54, 0.80),
        (0.50, 0.56), (0.46, 0.80), (0.38, 0.80), (0.34, 0.55),
    ],
    "sweater": [
        (0.28, 0.30), (0.19, 0.37), (0.13, 0.52), (0.22, 0.57), (0.29, 0.50),
        (0.29, 0.76), (0.71, 0.76), (0.71, 0.50), (0.78, 0.57), (0.87, 0.52),
        (0.81, 0.37), (0.72, 0.30), (0.50, 0.34),
    ],
    "coat": [
        (0.32, 0.25), (0.21, 0.32), (0.13, 0.48), (0.22, 0.54), (0.31, 0.47),
        (0.30, 0.84), (0.50, 0.82), (0.70, 0.84), (0.69, 0.47), (0.78, 0.54),
        (0.87, 0.48), (0.79, 0.32), (0.68, 0.25), (0.50, 0.30),
    ],
    "scarf": [
        (0.34, 0.28), (0.44, 0.30), (0.44, 0.66), (0.52, 0.80), (0.60, 0.66),
        (0.60, 0.30), (0.66, 0.28), (0.66, 0.70), (0.50, 0.86), (0.34, 0.70),
    ],
}

# Mot-clé de catégorie -> silhouette.
CATEGORY_GARMENT = {
    "robe": "dress", "blouse": "shirt", "haut": "tshirt", "jupe": "skirt",
    "manteau": "coat", "chemise": "shirt", "t-shirt": "tshirt", "tshirt": "tshirt",
    "pantalon": "pants", "chino": "pants", "veste": "coat", "pull": "sweater",
    "sweat": "sweater", "écharpe": "scarf", "echarpe": "scarf", "accessoire": "scarf",
}


def garment_for(text):
    low = (text or "").lower()
    for key, garment in CATEGORY_GARMENT.items():
        if key in low:
            return garment
    return "tshirt"


def generate_image(title, subtitle="", garment="tshirt", palette_index=0):
    """Retourne les octets PNG d'une image de démonstration."""
    top, bottom = PALETTES[palette_index % len(PALETTES)]
    img = _gradient(top, bottom).convert("RGBA")

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Silhouette du vêtement.
    points = _poly(GARMENTS.get(garment, GARMENTS["tshirt"]))
    odraw.polygon(points, fill=GARMENT_FILL, outline=GARMENT_OUTLINE)

    # Marque DressIT en haut.
    brand_font = _font(SERIF_BOLD, 40)
    odraw.text((40, 34), "DressIT", font=brand_font, fill=(255, 255, 255, 230))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Bandeau sombre en bas pour le texte.
    draw.rectangle([(0, HEIGHT - 150), (WIDTH, HEIGHT)], fill=(26, 15, 8, 200))

    title_font = _font(SERIF_BOLD, 46)
    sub_font = _font(SANS, 26)

    # Titre (tronqué si trop long).
    t = title if len(title) <= 26 else title[:25] + "…"
    draw.text((40, HEIGHT - 118), t, font=title_font, fill=(255, 255, 255, 255))
    if subtitle:
        draw.text((40, HEIGHT - 56), subtitle.upper(), font=sub_font, fill=(201, 162, 75, 255))

    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def compose_with_photo(photo_file, title="DressIT", subtitle="", palette_index=0):
    """Compose la photo d'un modèle sur un fond de marque avec bandeau et titre.

    Sert au Studio IA quand l'admin fournit la photo du modèle : on l'habille
    aux couleurs DressIT (fond dégradé, marque, bandeau titre) pour produire un
    visuel prêt à l'emploi.
    """
    top, bottom = PALETTES[palette_index % len(PALETTES)]
    canvas = _gradient(top, bottom).convert("RGB")

    try:
        photo = Image.open(photo_file).convert("RGB")
    except Exception:
        # Pas de photo exploitable : on retombe sur le générateur de silhouette.
        return generate_image(title, subtitle, "tshirt", palette_index)

    # Cadre la photo (couverture) dans une zone centrale.
    margin_x, top_y, bottom_y = 60, 120, HEIGHT - 170
    box_w, box_h = WIDTH - 2 * margin_x, bottom_y - top_y
    ratio = max(box_w / photo.width, box_h / photo.height)
    photo = photo.resize((int(photo.width * ratio), int(photo.height * ratio)))
    left = (photo.width - box_w) // 2
    upper = (photo.height - box_h) // 2
    photo = photo.crop((left, upper, left + box_w, upper + box_h))
    canvas.paste(photo, (margin_x, top_y))

    draw = ImageDraw.Draw(canvas)
    # Marque en haut.
    draw.text((40, 40), "DressIT", font=_font(SERIF_BOLD, 40), fill=(255, 255, 255))
    # Bandeau titre en bas.
    draw.rectangle([(0, HEIGHT - 150), (WIDTH, HEIGHT)], fill=(26, 15, 8))
    t = title if len(title) <= 26 else title[:25] + "…"
    draw.text((40, HEIGHT - 118), t, font=_font(SERIF_BOLD, 46), fill=(255, 255, 255))
    if subtitle:
        draw.text((40, HEIGHT - 56), subtitle.upper(), font=_font(SANS, 26), fill=(201, 162, 75))

    buf = BytesIO()
    canvas.save(buf, format="JPEG", quality=88)
    return buf.getvalue()
