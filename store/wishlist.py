"""Liste de favoris.

- Utilisateur connecté  -> stockée en base (modèle Favorite), persistante.
- Visiteur non connecté -> stockée dans la session.
"""

from .models import Favorite, Product

WISHLIST_SESSION_KEY = "wishlist"


class Wishlist:
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        if self.user is None:
            self.session = request.session
            if WISHLIST_SESSION_KEY not in self.session:
                self.session[WISHLIST_SESSION_KEY] = []

    # -- lecture --
    def product_ids(self):
        if self.user:
            return set(
                self.user.favorites.values_list("product_id", flat=True)
            )
        return set(self.session.get(WISHLIST_SESSION_KEY, []))

    def contains(self, product_id):
        return int(product_id) in self.product_ids()

    def products(self):
        ids = self.product_ids()
        return Product.objects.available().filter(id__in=ids).prefetch_related("images")

    def __len__(self):
        return len(self.product_ids())

    # -- écriture --
    def toggle(self, product):
        """Ajoute si absent, retire si présent. Retourne True si ajouté."""
        if self.user:
            fav, created = Favorite.objects.get_or_create(user=self.user, product=product)
            if not created:
                fav.delete()
                return False
            return True
        ids = self.session.get(WISHLIST_SESSION_KEY, [])
        if product.id in ids:
            ids.remove(product.id)
            added = False
        else:
            ids.append(product.id)
            added = True
        self.session[WISHLIST_SESSION_KEY] = ids
        self.session.modified = True
        return added

    def remove(self, product):
        if self.user:
            Favorite.objects.filter(user=self.user, product=product).delete()
        else:
            ids = self.session.get(WISHLIST_SESSION_KEY, [])
            if product.id in ids:
                ids.remove(product.id)
                self.session[WISHLIST_SESSION_KEY] = ids
                self.session.modified = True
