"""Modèles de la boutique DressIT."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    """Rayon du produit."""

    HOMME = "homme", _("Homme")
    FEMME = "femme", _("Femme")
    UNISEXE = "unisexe", _("Unisexe")


class Category(models.Model):
    """Catégorie de vêtements (ex : T-shirts, Robes, Pantalons)."""

    name = models.CharField(_("Nom"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True, blank=True)
    gender = models.CharField(
        _("Rayon"), max_length=10, choices=Gender.choices, default=Gender.UNISEXE
    )
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(
        _("Image de la catégorie"), upload_to="categories/", blank=True, null=True
    )
    order = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.name}-{self.gender}")
            slug, i = base, 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Size(models.Model):
    """Taille disponible (ex : XS, S, M, L, XL, 38, 40...)."""

    label = models.CharField(_("Taille"), max_length=10, unique=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)

    class Meta:
        verbose_name = _("Taille")
        verbose_name_plural = _("Tailles")
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class Color(models.Model):
    """Couleur disponible, avec un code hexadécimal pour l'affichage."""

    name = models.CharField(_("Nom de la couleur"), max_length=40, unique=True)
    hex_code = models.CharField(
        _("Code couleur (hex)"),
        max_length=7,
        default="#000000",
        help_text=_("Ex : #8B5E3C. Sert à afficher une pastille de couleur."),
    )

    class Meta:
        verbose_name = _("Couleur")
        verbose_name_plural = _("Couleurs")
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_active=True)

    def featured(self):
        return self.available().filter(is_featured=True)


class Product(models.Model):
    """Un article mis en vente."""

    name = models.CharField(_("Nom de l'article"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Catégorie"),
    )
    gender = models.CharField(
        _("Rayon"), max_length=10, choices=Gender.choices, default=Gender.UNISEXE
    )
    description = models.TextField(_("Description"), blank=True)

    price = models.DecimalField(_("Prix"), max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        _("Prix barré (avant promo)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Optionnel. Affiche une réduction si supérieur au prix."),
    )

    sizes = models.ManyToManyField(
        Size, blank=True, related_name="products", verbose_name=_("Tailles disponibles")
    )
    colors = models.ManyToManyField(
        Color, blank=True, related_name="products", verbose_name=_("Couleurs disponibles")
    )

    stock = models.PositiveIntegerField(_("Stock"), default=0)
    is_active = models.BooleanField(_("En vente"), default=True)
    is_featured = models.BooleanField(_("Mis en avant (accueil)"), default=False)

    created_at = models.DateTimeField(_("Ajouté le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, i = base, 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product", args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_on_sale(self):
        return bool(self.compare_at_price and self.compare_at_price > self.price)

    @property
    def discount_percent(self):
        if not self.is_on_sale:
            return 0
        return round((1 - (self.price / self.compare_at_price)) * 100)

    @property
    def main_image(self):
        img = self.images.first()
        return img.image if img else None


class ProductImage(models.Model):
    """Photo d'un article. Plusieurs photos possibles par article."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("Article")
    )
    image = models.ImageField(_("Photo"), upload_to="products/")
    alt = models.CharField(_("Texte alternatif"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("Ordre"), default=0)

    class Meta:
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
        ordering = ["order", "id"]

    def __str__(self):
        return f"Photo — {self.product.name}"


class Order(models.Model):
    """Commande passée par un client."""

    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        PAID = "paid", _("Payée")
        SHIPPED = "shipped", _("Expédiée")
        DELIVERED = "delivered", _("Livrée")
        CANCELLED = "cancelled", _("Annulée")

    class PaymentMethod(models.TextChoices):
        CARD = "card", _("Carte bancaire")
        COD = "cod", _("Paiement à la livraison")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Client"),
    )

    full_name = models.CharField(_("Nom complet"), max_length=150)
    email = models.EmailField(_("E-mail"))
    phone = models.CharField(_("Téléphone"), max_length=40)
    address = models.CharField(_("Adresse"), max_length=255)
    city = models.CharField(_("Ville"), max_length=100)
    postal_code = models.CharField(_("Code postal"), max_length=20)
    country = models.CharField(_("Pays"), max_length=100, default="France")
    note = models.TextField(_("Note (optionnel)"), blank=True)

    payment_method = models.CharField(
        _("Mode de paiement"),
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
    )
    status = models.CharField(
        _("Statut"), max_length=12, choices=Status.choices, default=Status.PENDING
    )
    paid = models.BooleanField(_("Payée"), default=False)

    created_at = models.DateTimeField(_("Passée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commande #{self.pk}"

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), start=0)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Ligne d'une commande (un article, une quantité, une variante)."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Commande")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name=_("Article"),
    )
    product_name = models.CharField(_("Nom de l'article"), max_length=200)
    price = models.DecimalField(_("Prix unitaire"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("Quantité"), default=1)
    size = models.CharField(_("Taille"), max_length=20, blank=True)
    color = models.CharField(_("Couleur"), max_length=40, blank=True)

    class Meta:
        verbose_name = _("Ligne de commande")
        verbose_name_plural = _("Lignes de commande")

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
