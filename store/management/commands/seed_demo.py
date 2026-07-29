"""Remplit la boutique avec des données de démonstration.

Usage :  python manage.py seed_demo
Ajoutez  --admin  pour créer aussi un compte administrateur (admin / admin12345).
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.models import Category, Color, Gender, Product, Size

SIZES = [("XS", 1), ("S", 2), ("M", 3), ("L", 4), ("XL", 5), ("XXL", 6),
         ("38", 10), ("40", 11), ("42", 12), ("44", 13)]

COLORS = [
    ("Noir", "#1c1c1c"), ("Blanc", "#f5f5f0"), ("Beige", "#d8c7a8"),
    ("Marron", "#5c4433"), ("Doré", "#c9a24b"), ("Camel", "#b3813d"),
    ("Bordeaux", "#6b2233"), ("Bleu marine", "#22314a"), ("Vert olive", "#4a5530"),
    ("Rose poudré", "#d8a7a0"),
]

CATEGORIES = [
    ("Robes", Gender.FEMME), ("Hauts & Blouses", Gender.FEMME),
    ("Jupes", Gender.FEMME), ("Manteaux Femme", Gender.FEMME),
    ("Chemises", Gender.HOMME), ("T-shirts Homme", Gender.HOMME),
    ("Pantalons Homme", Gender.HOMME), ("Vestes Homme", Gender.HOMME),
    ("Pulls & Sweats", Gender.UNISEXE), ("Accessoires", Gender.UNISEXE),
]

PRODUCTS = [
    ("Robe longue satinée", "Robes", Gender.FEMME, "24.90", "39.90",
     "Une robe fluide et élégante, parfaite pour les soirées comme pour le quotidien."),
    ("Blouse en lin beige", "Hauts & Blouses", Gender.FEMME, "16.90", "22.90",
     "Blouse légère en lin, coupe ample et confortable."),
    ("Jupe plissée dorée", "Jupes", Gender.FEMME, "19.90", None,
     "Jupe midi plissée aux reflets dorés, un incontournable chic."),
    ("Manteau camel long", "Manteaux Femme", Gender.FEMME, "49.90", "79.90",
     "Manteau chaud en laine mélangée, coupe droite intemporelle."),
    ("Chemise oxford blanche", "Chemises", Gender.HOMME, "18.90", "26.90",
     "Chemise classique en coton oxford, idéale au bureau comme en week-end."),
    ("T-shirt coton bio", "T-shirts Homme", Gender.HOMME, "9.90", None,
     "T-shirt tout doux en coton biologique, coupe régulière."),
    ("Chino beige", "Pantalons Homme", Gender.HOMME, "24.90", "34.90",
     "Pantalon chino polyvalent, tissu extensible pour un confort optimal."),
    ("Veste en velours côtelé", "Vestes Homme", Gender.HOMME, "39.90", "59.90",
     "Veste en velours côtelé marron, une pièce chaleureuse et raffinée."),
    ("Pull col rond maille douce", "Pulls & Sweats", Gender.UNISEXE, "22.90", "29.90",
     "Pull en maille douce, chaud et léger, unisexe."),
    ("Écharpe en laine dorée", "Accessoires", Gender.UNISEXE, "12.90", None,
     "Écharpe douce aux tons chauds pour sublimer toutes vos tenues."),
    ("Robe portefeuille", "Robes", Gender.FEMME, "21.90", "32.90",
     "Robe portefeuille flatteuse, ajustable à toutes les morphologies."),
    ("Sweat capuche premium", "Pulls & Sweats", Gender.UNISEXE, "27.90", None,
     "Sweat à capuche épais et confortable, molleton gratté."),
]


class Command(BaseCommand):
    help = "Crée des données de démonstration pour la boutique DressIT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin",
            action="store_true",
            help="Crée aussi un compte admin (admin / admin12345).",
        )

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
            cat, _ = Category.objects.get_or_create(
                name=name, gender=gender, defaults={"order": i}
            )
            cats[name] = cat

        clothing_sizes = ["XS", "S", "M", "L", "XL"]
        default_colors = ["Noir", "Beige", "Marron", "Doré"]

        created = 0
        for name, cat_name, gender, price, compare, desc in PRODUCTS:
            if Product.objects.filter(name=name).exists():
                continue
            p = Product.objects.create(
                name=name,
                category=cats[cat_name],
                gender=gender,
                description=desc,
                price=Decimal(price),
                compare_at_price=Decimal(compare) if compare else None,
                stock=25,
                is_active=True,
                is_featured=created < 6,
            )
            p.sizes.set([sizes[s] for s in clothing_sizes])
            p.colors.set([colors[c] for c in default_colors])
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✔ {len(sizes)} tailles, {len(colors)} couleurs, "
                f"{len(cats)} catégories, {created} nouveaux articles."
            )
        )

        if options["admin"]:
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@dressit.local", "admin12345")
                self.stdout.write(
                    self.style.WARNING(
                        "✔ Compte admin créé : identifiant « admin », mot de passe « admin12345 » "
                        "(à changer immédiatement)."
                    )
                )
            else:
                self.stdout.write("Le compte admin existe déjà.")

        self.stdout.write(
            self.style.NOTICE(
                "\nℹ Les articles n'ont pas encore de photo : ajoutez-les depuis "
                "l'admin (/admin) pour un rendu complet."
            )
        )
