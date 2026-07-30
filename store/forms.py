"""Formulaires de la boutique."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Category, Color, Complaint, Order, Product, PromoCode, Size


class StyledFormMixin:
    """Applique la classe CSS « input » à tous les champs texte du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(
                widget,
                (forms.RadioSelect, forms.CheckboxInput, forms.CheckboxSelectMultiple),
            ):
                continue
            css = "select" if isinstance(widget, forms.Select) else "input"
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css}".strip()


class SignUpForm(StyledFormMixin, UserCreationForm):
    """Inscription client avec e-mail."""

    first_name = forms.CharField(label=_("Prénom"), max_length=150, required=True)
    email = forms.EmailField(label=_("E-mail"), required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
        return user


class CheckoutForm(StyledFormMixin, forms.ModelForm):
    """Informations de livraison et paiement lors de la commande."""

    # Moyens de paiement proposés (l'ancienne « carte » reste en base mais
    # n'est plus offerte au client).
    PAYMENT_CHOICES = [
        (Order.PaymentMethod.WAVE, _("Wave")),
        (Order.PaymentMethod.ORANGE_MONEY, _("Orange Money")),
        (Order.PaymentMethod.COD, _("Paiement à la livraison")),
    ]

    payment_method = forms.ChoiceField(
        label=_("Mode de paiement"),
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        initial=Order.PaymentMethod.WAVE,
    )

    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
            "note",
            "payment_method",
        ]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class ComplaintForm(StyledFormMixin, forms.ModelForm):
    """Réclamation client (SAV)."""

    class Meta:
        model = Complaint
        fields = ["name", "email", "phone", "subject", "order", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].required = False
        self.fields["phone"].required = False
        # Un client connecté ne voit que ses propres commandes.
        if user is not None and user.is_authenticated:
            self.fields["order"].queryset = user.orders.all()
        else:
            from .models import Order

            self.fields["order"].queryset = Order.objects.none()
            self.fields["order"].widget = forms.HiddenInput()


class ProductForm(StyledFormMixin, forms.ModelForm):
    """Ajout / modification d'un article depuis le back-office DressIT."""

    class Meta:
        model = Product
        fields = [
            "name", "category", "gender", "description", "price",
            "compare_at_price", "sizes", "colors",
            "sold_out_sizes", "sold_out_colors", "stock",
            "is_active", "is_featured",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "sizes": forms.CheckboxSelectMultiple,
            "colors": forms.CheckboxSelectMultiple,
            "sold_out_sizes": forms.CheckboxSelectMultiple,
            "sold_out_colors": forms.CheckboxSelectMultiple,
        }


class CategoryForm(StyledFormMixin, forms.ModelForm):
    """Ajout / modification d'une catégorie."""

    class Meta:
        model = Category
        fields = ["name", "gender", "description", "image", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OrderStatusForm(StyledFormMixin, forms.ModelForm):
    """Mise à jour du statut (et du paiement) d'une commande côté back-office."""

    class Meta:
        model = Order
        fields = ["status", "paid"]


class SizeForm(StyledFormMixin, forms.ModelForm):
    """Ajout / modification d'une taille."""

    class Meta:
        model = Size
        fields = ["label", "order"]


class ColorForm(StyledFormMixin, forms.ModelForm):
    """Ajout / modification d'une couleur."""

    class Meta:
        model = Color
        fields = ["name", "hex_code"]
        widgets = {
            "hex_code": forms.TextInput(attrs={"type": "color"}),
        }


class ComplaintReplyForm(StyledFormMixin, forms.ModelForm):
    """Réponse du service client à une réclamation (back-office)."""

    class Meta:
        model = Complaint
        fields = ["status", "response"]
        widgets = {
            "response": forms.Textarea(attrs={"rows": 6}),
        }


class PromoCodeForm(StyledFormMixin, forms.ModelForm):
    """Ajout / modification d'un code promo."""

    class Meta:
        model = PromoCode
        fields = [
            "code", "discount_type", "value", "min_subtotal",
            "active", "valid_until", "max_uses",
        ]
        widgets = {
            "valid_until": forms.DateInput(attrs={"type": "date"}),
        }
