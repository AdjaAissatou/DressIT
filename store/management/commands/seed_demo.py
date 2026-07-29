"""Remplit la boutique avec des données de démonstration.

Usage :  python manage.py seed_demo
Options :
  --admin      crée aussi un compte administrateur (admin / admin12345)
  --no-images  n'attache pas les photos de démonstration

Les prix sont exprimés en Franc CFA (XOF).
"""

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from store.models import Category, Color, Gender, Product, ProductImage, PromoCode, Size
from store.placeholder_images import garment_for, generate_image

PHOTOS_DIR = Path(settings.BASE_DIR) / "store" / "demo_photos"

SIZES = [("XS", 1), ("S", 2), ("M", 3), ("L", 4), ("XL", 5), ("XXL", 6),
         ("38", 10), ("40", 11), ("42", 12), ("44", 13)]

COLORS = [
    ("Noir", "#1c1c1c"), ("Blanc", "#f5f5f0"), ("Beige", "#d8c7a8"),
    ("Marron", "#5c4433"), ("Doré", "#c9a24b"), ("Camel", "#b3813d"),
    ("Bordeaux", "#6b2233"), ("Bleu marine", "#22314a"), ("Vert émeraude", "#1f7a5f"),
    ("Rose poudré", "#d8a7a0"),
]

CATEGORIES = [
    ("Robes", Gender.FEMME), ("Hauts & Blouses", Gender.FEMME),
    ("Jupes", Gender.FEMME), ("Manteaux Femme", Gender.FEMME),
    ("Chemises", Gender.HOMME), ("T-shirts Homme", Gender.HOMME),
    ("Pantalons Homme", Gender.HOMME), ("Vestes Homme", Gender.HOMME),
    ("Pulls & Sweats", Gender.UNISEXE), ("Accessoires", Gender.UNISEXE),
]

# (nom, catégorie, rayon, prix, prix_barré, description, [photos]) — prix en FCFA.
PRODUCTS = [
    ("Robe longue satinée", "Robes", Gender.FEMME, "15900", "24900",
     "Une robe fluide et élégante, parfaite pour les soirées comme pour le quotidien.",
     ["dress2", "dress0", "dress4"]),
    ("Blouse en lin beige", "Hauts & Blouses", Gender.FEMME, "9900", "13900",
     "Blouse légère en lin, coupe ample et confortable.",
     ["shirt1", "shirt0", "shirt5"]),
    ("Jupe plissée dorée", "Jupes", Gender.FEMME, "12900", None,
     "Jupe midi plissée aux reflets dorés, un incontournable chic.",
     ["skirt0", "skirt1", "skirt3"]),
    ("Manteau camel long", "Manteaux Femme", Gender.FEMME, "32900", "49900",
     "Manteau chaud en laine mélangée, coupe droite intemporelle.",
     ["coat4", "coat1", "coat3"]),
    ("Chemise oxford blanche", "Chemises", Gender.HOMME, "11900", "16900",
     "Chemise classique en coton oxford, idéale au bureau comme en week-end.",
     ["shirt3", "shirt4", "shirt1"]),
    ("T-shirt coton bio", "T-shirts Homme", Gender.HOMME, "5900", None,
     "T-shirt tout doux en coton biologique, coupe régulière.",
     ["tshirt0", "tshirt3", "tshirt1"]),
    ("Chino beige", "Pantalons Homme", Gender.HOMME, "15900", "21900",
     "Pantalon chino polyvalent, tissu extensible pour un confort optimal.",
     ["pants3", "pants5", "pants0"]),
    ("Veste en velours côtelé", "Vestes Homme", Gender.HOMME, "25900", "38900",
     "Veste en velours côtelé, une pièce chaleureuse et raffinée.",
     ["coat2", "coat3", "coat0"]),
    ("Pull col rond maille douce", "Pulls & Sweats", Gender.UNISEXE, "14900", "18900",
     "Pull en maille douce, chaud et léger, unisexe.",
     ["sweater4", "sweater2", "sweater1"]),
    ("Écharpe en laine dorée", "Accessoires", Gender.UNISEXE, "7900", None,
     "Écharpe douce aux tons chauds pour sublimer toutes vos tenues.",
     ["scarf0"]),
    ("Robe portefeuille", "Robes", Gender.FEMME, "13900", "20900",
     "Robe portefeuille flatteuse, ajustable à toutes les morphologies.",
     ["dress3", "dress5", "dress1"]),
    ("Sweat capuche premium", "Pulls & Sweats", Gender.UNISEXE, "17900", None,
     "Sweat à capuche épais et confortable, molleton gratté.",
     ["sweater1", "sweater4", "sweater2"]),
]


class Command(BaseCommand):
    help = "Crée des données de démonstration pour la boutique DressIT (prix en FCFA)."

    def add_arguments(self, parser):
        parser.add_argument("--admin", action="store_true",
                            help="Crée aussi un compte admin (admin / admin12345).")
        parser.add_argument("--no-images", action="store_true",
                            help="Ne pas attacher les photos de démonstration.")

    def _attach_photos(self, product, photo_names, idx):
        """Attache les vraies photos ; retombe sur une image générée si absentes."""
        attached = 0
        for order, name in enumerate(photo_names):
            path = PHOTOS_DIR / f"{name}.jpg"
            if path.exists():
                with open(path, "rb") as fh:
                    img = ProductImage(product=product, alt=product.name, order=order)
                    img.image.save(f"{product.slug}-{order}.jpg", ContentFile(fh.read()), save=True)
                attached += 1
        if attached == 0:  # aucune vraie photo -> image générée
            data = generate_image(product.name, product.category.name,
                                  garment_for(f"{product.name} {product.category.name}"), idx)
            img = ProductImage(product=product, alt=product.name)
            img.image.save(f"demo-{product.slug}.jpg", ContentFile(data), save=True)

    def handle(self, *args, **options):
        sizes = {}
        for label, order in SIZES:
            s, _ = Size.objects.get_or_create(label=label, defaults={"order": order})
            sizes[label] = s

        colors = {}
        for name, hex_code in COLORS:
            c, _ = Color.objects.get_or_create(name=name, defaults={"hex_code": hex_code})
            colors[name] = c

        cats = {}
        for i, (name, gender) in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(name=name, gender=gender, defaults={"order": i})
            cats[name] = cat

        clothing_sizes = ["XS", "S", "M", "L", "XL"]
        default_colors = ["Noir", "Beige", "Camel", "Doré"]
        make_images = not options["no_images"]

        created = 0
        for idx, (name, cat_name, gender, price, compare, desc, photos) in enumerate(PRODUCTS):
            if Product.objects.filter(name=name).exists():
                continue
            p = Product.objects.create(
                name=name, category=cats[cat_name], gender=gender, description=desc,
                price=Decimal(price),
                compare_at_price=Decimal(compare) if compare else None,
                stock=25, is_active=True, is_featured=created < 6,
            )
            p.sizes.set([sizes[s] for s in clothing_sizes])
            p.colors.set([colors[c] for c in default_colors])
            if make_images and not p.images.exists():
                self._attach_photos(p, photos, idx)
            created += 1

        # Image de chaque catégorie = 1re photo d'un de ses articles.
        if make_images:
            for cat in cats.values():
                if not cat.image:
                    sample = cat.products.first()
                    if sample and sample.main_image:
                        with sample.main_image.open("rb") as fh:
                            cat.image.save(f"cat-{cat.slug}.jpg", ContentFile(fh.read()), save=True)

        # Codes promo de démonstration (montants en FCFA).
        promos = [
            ("BIENVENUE10", PromoCode.DiscountType.PERCENT, Decimal("10"), Decimal("0"), None),
            ("ETE20", PromoCode.DiscountType.PERCENT, Decimal("20"), Decimal("25000"),
             timezone.now().date() + timedelta(days=60)),
            ("MOINS2000", PromoCode.DiscountType.FIXED, Decimal("2000"), Decimal("15000"), None),
        ]
        promo_created = 0
        for code, dtype, value, min_sub, until in promos:
            _, was_created = PromoCode.objects.get_or_create(
                code=code,
                defaults={"discount_type": dtype, "value": value,
                          "min_subtotal": min_sub, "valid_until": until, "active": True},
            )
            promo_created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f"✔ {len(sizes)} tailles, {len(colors)} couleurs, {len(cats)} catégories, "
            f"{created} nouveaux articles, {promo_created} codes promo."
        ))

        if options["admin"]:
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@dressit.local", "admin12345")
                self.stdout.write(self.style.WARNING(
                    "✔ Compte admin créé : « admin » / « admin12345 » (à changer)."
                ))
            else:
                self.stdout.write("Le compte admin existe déjà.")

        self.stdout.write(self.style.NOTICE(
            "\nℹ Vraies photos de démonstration attachées. Remplacez-les par vos "
            "propres photos depuis l'admin (/admin)."
        ))
