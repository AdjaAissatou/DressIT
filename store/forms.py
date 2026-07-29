"""Formulaires de la boutique."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Order


class StyledFormMixin:
    """Applique la classe CSS « input » à tous les champs texte du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.RadioSelect, forms.CheckboxInput)):
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
            "payment_method": forms.RadioSelect(),
        }
