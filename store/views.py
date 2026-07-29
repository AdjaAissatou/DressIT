"""Vues de la boutique DressIT."""

import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import imagesearch, payments
from .cart import Cart
from .emails import send_complaint_received, send_order_confirmation, send_payment_confirmation
from .forms import CheckoutForm, ComplaintForm, SignUpForm
from .models import Category, Gender, Order, OrderItem, Product, PromoCode
from .wishlist import Wishlist


def home(request):
    featured = Product.objects.featured().prefetch_related("images")[:8]
    new_arrivals = Product.objects.available().prefetch_related("images")[:8]
    on_sale = [
        p for p in Product.objects.available().prefetch_related("images") if p.is_on_sale
    ][:8]
    # Un code promo à mettre en avant sur la page d'accueil, s'il en existe un actif.
    highlight_promo = PromoCode.objects.filter(active=True).order_by("-id").first()
    context = {
        "featured": featured,
        "new_arrivals": new_arrivals,
        "on_sale": on_sale,
        "highlight_promo": highlight_promo,
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
            method = form.cleaned_data["payment_method"]

            # Vérifie que la passerelle choisie est bien configurée (pas de faux paiement).
            if method == Order.PaymentMethod.WAVE and not payments.wave_enabled():
                messages.error(request, _("Le paiement Wave n'est pas encore configuré."))
                return render(request, "store/checkout.html", _checkout_ctx(form))
            if method == Order.PaymentMethod.ORANGE_MONEY and not payments.om_enabled():
                messages.error(request, _("Le paiement Orange Money n'est pas encore configuré."))
                return render(request, "store/checkout.html", _checkout_ctx(form))

            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            promo = cart.promo
            order.shipping_cost = cart.shipping
            order.discount = cart.discount
            order.promo_code = promo.code if promo else ""
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
            if promo:
                promo.used_count = promo.used_count + 1
                promo.save(update_fields=["used_count"])

            # Paiement à la livraison : commande ferme, stock réservé tout de suite.
            if method == Order.PaymentMethod.COD:
                _commit_stock(order)
                cart.clear()
                cart.remove_promo()
                send_order_confirmation(order, request)
                messages.success(
                    request,
                    _("Merci ! Votre commande #%(id)s a bien été enregistrée.")
                    % {"id": order.id},
                )
                return redirect("order_confirmation", order_id=order.id)

            # Paiement en ligne : redirection vers la passerelle (Wave / Orange Money).
            try:
                if method == Order.PaymentMethod.WAVE:
                    url = payments.wave_create_session(order, request)
                else:
                    url = payments.om_create_payment(order, request)
            except payments.PaymentError as exc:
                order.delete()  # rien n'a été réservé ni encaissé
                messages.error(
                    request,
                    _("Le paiement n'a pas pu être initié : %(e)s") % {"e": exc},
                )
                return render(request, "store/checkout.html", _checkout_ctx(form))

            cart.clear()
            cart.remove_promo()
            return redirect(url)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", _checkout_ctx(form))


def _checkout_ctx(form):
    return {
        "form": form,
        "wave_enabled": payments.wave_enabled(),
        "om_enabled": payments.om_enabled(),
    }


def _commit_stock(order):
    """Décrémente le stock une seule fois pour une commande."""
    if order.stock_committed:
        return
    for item in order.items.select_related("product"):
        if item.product:
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save(update_fields=["stock"])
    order.stock_committed = True
    order.save(update_fields=["stock_committed"])


def _mark_paid(order, request=None):
    """Marque une commande payée (idempotent) : stock + e-mail."""
    if order.paid:
        return
    order.paid = True
    order.status = Order.Status.PAID
    order.save(update_fields=["paid", "status"])
    _commit_stock(order)
    send_payment_confirmation(order, request)


# --------------------------------------------------------------------------- #
# Retours et webhooks des passerelles de paiement
# --------------------------------------------------------------------------- #
def payment_return(request, order_id):
    """Retour du client depuis Wave / Orange Money : on vérifie l'état RÉEL."""
    order = get_object_or_404(Order, id=order_id)
    gw = request.GET.get("gw")
    try:
        if gw == "wave":
            ok = payments.wave_payment_status(order) == "succeeded"
        elif gw == "om":
            ok = payments.om_payment_status(order) in ("SUCCESS", "SUCCESSFULL")
        else:
            ok = False
    except payments.PaymentError:
        ok = False

    if ok:
        _mark_paid(order, request)
        messages.success(request, _("Paiement confirmé, merci !"))
    else:
        messages.info(
            request,
            _("Votre paiement est en cours de vérification. Vous recevrez une confirmation."),
        )
    return redirect("order_confirmation", order_id=order.id)


def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    messages.warning(request, _("Paiement annulé. Votre commande n'a pas été validée."))
    return render(request, "store/payment_cancel.html", {"order": order})


@csrf_exempt
@require_POST
def wave_webhook(request):
    raw = request.body.decode("utf-8", errors="replace")
    if not payments.wave_verify_webhook(raw, request.headers.get("Wave-Signature", "")):
        return HttpResponse(status=400)
    try:
        event = json.loads(raw)
    except ValueError:
        return HttpResponse(status=400)
    data = event.get("data", event)
    if data.get("payment_status") == "succeeded":
        ref = data.get("client_reference") or ""
        order = Order.objects.filter(id=ref).first() or Order.objects.filter(
            gateway_session_id=data.get("id", "")
        ).first()
        if order:
            _mark_paid(order)
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def om_webhook(request):
    try:
        data = json.loads(request.body.decode("utf-8", errors="replace"))
    except ValueError:
        return HttpResponse(status=400)
    order = Order.objects.filter(id=data.get("order_id", "")).first()
    if not order:
        return HttpResponse(status=404)
    # Vérifie le jeton de notification pour authentifier l'appel.
    notif = data.get("notif_token") or data.get("notiftoken")
    if order.gateway_notif_token and notif and notif != order.gateway_notif_token:
        return HttpResponse(status=400)
    if str(data.get("status", "")).upper() in ("SUCCESS", "SUCCESSFULL"):
        _mark_paid(order)
    return HttpResponse(status=200)


# --------------------------------------------------------------------------- #
# Recherche par photo
# --------------------------------------------------------------------------- #
def photo_search(request):
    results = None
    if request.method == "POST" and request.FILES.get("photo"):
        matches = imagesearch.search(request.FILES["photo"])
        results = [p for p, dist in matches if dist <= imagesearch.MATCH_THRESHOLD]
        if not results and matches:
            # Rien sous le seuil : propose tout de même les plus proches.
            results = [p for p, _d in matches[:8]]
    return render(request, "store/photo_search.html", {"results": results})


# --------------------------------------------------------------------------- #
# Codes promo
# --------------------------------------------------------------------------- #
@require_POST
def promo_apply(request):
    cart = Cart(request)
    ok, msg = cart.apply_promo(request.POST.get("code", ""))
    (messages.success if ok else messages.error)(request, msg)
    return redirect("cart")


@require_POST
def promo_remove(request):
    Cart(request).remove_promo()
    messages.info(request, _("Code promo retiré."))
    return redirect("cart")


# --------------------------------------------------------------------------- #
# Favoris (wishlist)
# --------------------------------------------------------------------------- #
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product.objects.available(), id=product_id)
    wishlist = Wishlist(request)
    added = wishlist.toggle(product)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"added": added, "count": len(wishlist)})
    messages.success(
        request,
        _("Ajouté à vos favoris ❤️") if added else _("Retiré de vos favoris."),
    )
    return redirect(request.META.get("HTTP_REFERER", "home"))


def wishlist_detail(request):
    wishlist = Wishlist(request)
    return render(
        request, "store/wishlist.html", {"products": wishlist.products()}
    )


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
    complaints = request.user.complaints.all()
    return render(
        request, "store/account.html", {"orders": orders, "complaints": complaints}
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})


# --------------------------------------------------------------------------- #
# Réclamations (SAV)
# --------------------------------------------------------------------------- #
def complaint_create(request):
    initial = {}
    order_id = request.GET.get("order")
    if request.user.is_authenticated:
        initial = {
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
        }
        if order_id:
            initial["order"] = order_id

    if request.method == "POST":
        form = ComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            if request.user.is_authenticated:
                complaint.user = request.user
            complaint.save()
            send_complaint_received(complaint, request)
            messages.success(
                request,
                _("Votre réclamation #%(id)s a bien été envoyée. Nous vous répondrons vite.")
                % {"id": complaint.id},
            )
            return redirect("account" if request.user.is_authenticated else "home")
    else:
        form = ComplaintForm(initial=initial, user=request.user)
    return render(request, "store/complaint.html", {"form": form})
