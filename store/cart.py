"""Panier stocké en session (aucun compte requis pour ajouter au panier)."""

from decimal import Decimal

from django.conf import settings

from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """Encapsule le panier stocké dans la session Django."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    @staticmethod
    def _key(product_id, size, color):
        return f"{product_id}|{size or ''}|{color or ''}"

    def add(self, product, quantity=1, size="", color="", override=False):
        key = self._key(product.id, size, color)
        if key not in self.cart:
            self.cart[key] = {
                "product_id": product.id,
                "price": str(product.price),
                "quantity": 0,
                "size": size,
                "color": color,
            }
        if override:
            self.cart[key]["quantity"] = quantity
        else:
            self.cart[key]["quantity"] += quantity
        if self.cart[key]["quantity"] <= 0:
            self.remove(key)
        self.save()

    def set_quantity(self, key, quantity):
        if key in self.cart:
            if quantity <= 0:
                self.remove(key)
            else:
                self.cart[key]["quantity"] = quantity
                self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = self.cart = {}
        self.save()

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = [item["product_id"] for item in self.cart.values()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        for key, item in self.cart.items():
            product = products.get(item["product_id"])
            if product is None:
                continue
            price = Decimal(item["price"])
            quantity = item["quantity"]
            yield {
                "key": key,
                "product": product,
                "price": price,
                "quantity": quantity,
                "size": item.get("size", ""),
                "color": item.get("color", ""),
                "subtotal": price * quantity,
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total(self):
        return sum(
            (Decimal(item["price"]) * item["quantity"] for item in self.cart.values()),
            start=Decimal("0"),
        )

    @property
    def currency(self):
        return settings.DRESSIT_CURRENCY_SYMBOL
