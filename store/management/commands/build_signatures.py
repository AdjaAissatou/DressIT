"""(Re)calcule les empreintes visuelles des photos pour la recherche par photo.

Usage :  python manage.py build_signatures [--all]
  --all  recalcule aussi les photos qui ont déjà une empreinte.
"""

from django.core.management.base import BaseCommand

from store.imagesearch import compute_signature
from store.models import ProductImage


class Command(BaseCommand):
    help = "Calcule les empreintes visuelles des photos d'articles."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Recalcule tout.")

    def handle(self, *args, **options):
        qs = ProductImage.objects.all()
        if not options["all"]:
            qs = qs.filter(signature="")
        done = 0
        for img in qs:
            try:
                sig = compute_signature(img.image.path)
            except (ValueError, OSError):
                sig = ""
            if sig:
                ProductImage.objects.filter(pk=img.pk).update(signature=sig)
                done += 1
        self.stdout.write(self.style.SUCCESS(f"✔ {done} empreintes calculées."))
