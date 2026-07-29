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
    # Empreinte visuelle pour la recherche par photo (calculée automatiquement).
    signature = models.TextField(_("Empreinte visuelle"), blank=True, default="")

    class Meta:
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
        ordering = ["order", "id"]

    def __str__(self):
        return f"Photo — {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.signature:
            from .imagesearch import compute_signature

            try:
                sig = compute_signature(self.image.path)
            except (NotImplementedError, ValueError, OSError):
                sig = ""
            if sig:
                # update_fields évite la récursion infinie via save().
                type(self).objects.filter(pk=self.pk).update(signature=sig)
                self.signature = sig


class Order(models.Model):
    """Commande passée par un client."""

    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        PAID = "paid", _("Payée")
        SHIPPED = "shipped", _("Expédiée")
        DELIVERED = "delivered", _("Livrée")
        CANCELLED = "cancelled", _("Annulée")

    class PaymentMethod(models.TextChoices):
        WAVE = "wave", _("Wave")
        ORANGE_MONEY = "orange_money", _("Orange Money")
        COD = "cod", _("Paiement à la livraison")
        CARD = "card", _("Carte bancaire")  # conservé pour l'historique

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
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.WAVE,
    )
    status = models.CharField(
        _("Statut"), max_length=12, choices=Status.choices, default=Status.PENDING
    )
    paid = models.BooleanField(_("Payée"), default=False)

    shipping_cost = models.DecimalField(
        _("Frais de livraison"), max_digits=10, decimal_places=2, default=0
    )
    discount = models.DecimalField(
        _("Remise"), max_digits=10, decimal_places=2, default=0
    )
    promo_code = models.CharField(_("Code promo utilisé"), max_length=40, blank=True)

    # Suivi du paiement en ligne (Wave / Orange Money).
    gateway_session_id = models.CharField(_("Réf. session paiement"), max_length=120, blank=True)
    gateway_token = models.CharField(_("Jeton de paiement"), max_length=255, blank=True)
    gateway_notif_token = models.CharField(_("Jeton de notification"), max_length=255, blank=True)
    stock_committed = models.BooleanField(_("Stock décrémenté"), default=False)

    created_at = models.DateTimeField(_("Passée le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commande #{self.pk}"

    @property
    def subtotal(self):
        return sum((item.subtotal for item in self.items.all()), start=0)

    @property
    def total(self):
        return self.subtotal - self.discount + self.shipping_cost

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


class PromoCode(models.Model):
    """Code promotionnel appliqué au panier (pourcentage ou montant fixe)."""

    class DiscountType(models.TextChoices):
        PERCENT = "percent", _("Pourcentage (%)")
        FIXED = "fixed", _("Montant fixe")

    code = models.CharField(_("Code"), max_length=40, unique=True)
    discount_type = models.CharField(
        _("Type de remise"),
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT,
    )
    value = models.DecimalField(
        _("Valeur"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Ex : 10 = -10 % ou -10 € selon le type."),
    )
    min_subtotal = models.DecimalField(
        _("Sous-total minimum"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Montant minimum du panier pour utiliser le code."),
    )
    active = models.BooleanField(_("Actif"), default=True)
    valid_until = models.DateField(_("Valable jusqu'au"), blank=True, null=True)
    max_uses = models.PositiveIntegerField(
        _("Nombre d'utilisations max"),
        blank=True,
        null=True,
        help_text=_("Laisser vide pour un usage illimité."),
    )
    used_count = models.PositiveIntegerField(_("Utilisé (fois)"), default=0)

    class Meta:
        verbose_name = _("Code promo")
        verbose_name_plural = _("Codes promo")
        ordering = ["-id"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def check_validity(self, subtotal):
        """Retourne (valide: bool, message d'erreur ou "")."""
        from django.utils import timezone

        if not self.active:
            return False, _("Ce code n'est plus actif.")
        if self.valid_until and self.valid_until < timezone.now().date():
            return False, _("Ce code a expiré.")
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False, _("Ce code a atteint sa limite d'utilisation.")
        if subtotal < self.min_subtotal:
            return False, _("Ce code nécessite un panier d'au moins %(min)s.") % {
                "min": self.min_subtotal
            }
        return True, ""

    def compute_discount(self, subtotal):
        from decimal import Decimal

        if self.discount_type == self.DiscountType.PERCENT:
            amount = subtotal * self.value / Decimal("100")
        else:
            amount = self.value
        # La remise ne peut pas dépasser le sous-total.
        return min(amount, subtotal).quantize(Decimal("0.01"))


class Complaint(models.Model):
    """Réclamation d'un client (SAV)."""

    class Status(models.TextChoices):
        OPEN = "open", _("Ouverte")
        IN_PROGRESS = "in_progress", _("En cours")
        RESOLVED = "resolved", _("Résolue")
        CLOSED = "closed", _("Fermée")

    class Subject(models.TextChoices):
        ORDER = "order", _("Problème de commande")
        DELIVERY = "delivery", _("Livraison")
        PRODUCT = "product", _("Article défectueux")
        PAYMENT = "payment", _("Paiement")
        REFUND = "refund", _("Remboursement / échange")
        OTHER = "other", _("Autre")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
        verbose_name=_("Client"),
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints",
        verbose_name=_("Commande concernée"),
    )
    name = models.CharField(_("Nom"), max_length=150)
    email = models.EmailField(_("E-mail"))
    phone = models.CharField(_("Téléphone"), max_length=40, blank=True)
    subject = models.CharField(
        _("Motif"), max_length=20, choices=Subject.choices, default=Subject.ORDER
    )
    message = models.TextField(_("Votre message"))

    status = models.CharField(
        _("Statut"), max_length=12, choices=Status.choices, default=Status.OPEN
    )
    response = models.TextField(_("Réponse du service client"), blank=True)

    created_at = models.DateTimeField(_("Reçue le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mise à jour"), auto_now=True)
    responded_at = models.DateTimeField(_("Répondue le"), null=True, blank=True)

    class Meta:
        verbose_name = _("Réclamation")
        verbose_name_plural = _("Réclamations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Réclamation #{self.pk} — {self.get_subject_display()}"


class Favorite(models.Model):
    """Article mis en favori par un utilisateur connecté."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("Client"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Article"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Favori")
        verbose_name_plural = _("Favoris")
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
