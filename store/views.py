"""Vues de la boutique DressIT."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, SignUpForm
from .models import Category, Gender, Order, OrderItem, Product


def home(request):
    featured = Product.objects.featured().prefetch_related("images")[:8]
    new_arrivals = Product.objects.available().prefetch_related("images")[:8]
    on_sale = [
        p for p in Product.objects.available().prefetch_related("images") if p.is_on_sale
    ][:8]
    context = {
        "featured": featured,
        "new_arrivals": new_arrivals,
        "on_sale": on_sale,
        "categories_homme": Category.objects.filter(gender__in=[Gender.HOMME, Gender.UNISEXE]),
        "categories_femme": Category.objects.filter(gender__in=[Gender.FEMME, Gender.UNISEXE]),
    }
    return render(request, "store/home.html", context)


def _filter_products(request, base_qs):
    """Applique recherche, tri et filtres à un queryset de produits."""
    products = base_qs.prefetch_related("images")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    sort = request.GET.get("sort", "recent")
    sort_map = {
        "recent": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))
    return products, query, sort


def product_list(request, gender=None):
    """Catalogue global ou par rayon (homme/femme)."""
    base = Product.objects.available()
    title = _("Boutique")
    if gender == Gender.HOMME:
        base = base.filter(gender__in=[Gender.HOMME, Gender.UNISEXE])
        title = _("Homme")
        categories = Category.objects.filter(gender__in=[Gender.HOMME, Gender.UNISEXE])
    elif gender == Gender.FEMME:
        base = base.filter(gender__in=[Gender.FEMME, Gender.UNISEXE])
        title = _("Femme")
        categories = Category.objects.filter(gender__in=[Gender.FEMME, Gender.UNISEXE])
    else:
        categories = Category.objects.all()

    products, query, sort = _filter_products(request, base)
    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get("page"))

    context = {
        "title": title,
        "gender": gender,
        "page_obj": page,
        "products": page.object_list,
        "categories": categories,
        "query": query,
        "sort": sort,
        "active_category": request.GET.get("category", ""),
    }
    return render(request, "store/product_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products, query, sort = _filter_products(request, category.products.available())
    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "title": category.name,
        "category": category,
        "page_obj": page,
        "products": page.object_list,
        "query": query,
        "sort": sort,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.available().prefetch_related("images", "sizes", "colors"),
        slug=slug,
    )
    related = (
        Product.objects.available()
        .filter(category=product.category)
        .exclude(pk=product.pk)
        .prefetch_related("images")[:4]
    )
    return render(
        request, "store/product_detail.html", {"product": product, "related": related}
    )


# --------------------------------------------------------------------------- #
# Panier
# --------------------------------------------------------------------------- #
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.available(), id=product_id)
    cart = Cart(request)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1
    size = request.POST.get("size", "")
    color = request.POST.get("color", "")
    cart.add(product, quantity=quantity, size=size, color=color)
    messages.success(
        request, _("« %(name)s » a été ajouté au panier.") % {"name": product.name}
    )
    if request.POST.get("next") == "detail":
        return redirect(product.get_absolute_url())
    return redirect("cart")


def cart_detail(request):
    return render(request, "store/cart.html", {})


@require_POST
def cart_update(request, key):
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    cart.set_quantity(key, quantity)
    return redirect("cart")


@require_POST
def cart_remove(request, key):
    Cart(request).remove(key)
    messages.info(request, _("Article retiré du panier."))
    return redirect("cart")


# --------------------------------------------------------------------------- #
# Commande & paiement
# --------------------------------------------------------------------------- #
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, _("Votre panier est vide."))
        return redirect("cart")

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "full_name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
        }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            # Paiement carte : simulation d'un paiement réussi (à remplacer par
            # Stripe/PayPal en production). Paiement à la livraison : non payé.
            if order.payment_method == Order.PaymentMethod.CARD:
                order.paid = True
                order.status = Order.Status.PAID
            else:
                order.paid = False
                order.status = Order.Status.PENDING
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    price=item["price"],
                    quantity=item["quantity"],
                    size=item["size"],
                    color=item["color"],
                )
                # Décrémente le stock
                product = item["product"]
                product.stock = max(0, product.stock - item["quantity"])
                product.save(update_fields=["stock"])

            cart.clear()
            messages.success(
                request,
                _("Merci ! Votre commande #%(id)s a bien été enregistrée.")
                % {"id": order.id},
            )
            return redirect("order_confirmation", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {"form": form})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Sécurité : un utilisateur connecté ne voit que ses commandes ;
    # un invité voit la commande juste après l'avoir passée.
    if request.user.is_authenticated:
        if order.user and order.user != request.user and not request.user.is_staff:
            messages.error(request, _("Commande introuvable."))
            return redirect("home")
    return render(request, "store/order_confirmation.html", {"order": order})


# --------------------------------------------------------------------------- #
# Comptes clients
# --------------------------------------------------------------------------- #
def signup(request):
    if request.user.is_authenticated:
        return redirect("account")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Bienvenue chez DressIT, votre compte a été créé !"))
            return redirect("account")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def account(request):
    orders = request.user.orders.prefetch_related("items").all()
    return render(request, "store/account.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})
