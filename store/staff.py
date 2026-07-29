"""Espace de gestion (staff) : tableau de bord, statistiques, stock.

Réservé aux membres du personnel (is_staff). Complète l'administration Django
avec une vue synthétique et des outils propres à la boutique.
"""

import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages as flash
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext as _

from . import ai
from .models import Category, Order, OrderItem, Product, ProductImage
from .placeholder_images import GARMENTS, compose_with_photo, generate_image

LOW_STOCK_THRESHOLD = 5

# Le Studio IA est réservé au super-administrateur (vous).
superadmin_required = user_passes_test(lambda u: u.is_active and u.is_superuser)


@staff_member_required
def dashboard(request):
    now = timezone.now()
    since_30 = now - timedelta(days=30)

    paid_orders = Order.objects.filter(paid=True)

    # Chiffre d'affaires (les totaux incluent remise + livraison).
    revenue = sum((o.total for o in paid_orders), Decimal("0"))
    revenue_30 = sum(
        (o.total for o in paid_orders.filter(created_at__gte=since_30)), Decimal("0")
    )

    orders_total = Order.objects.count()
    orders_pending = Order.objects.filter(status=Order.Status.PENDING).count()
    customers = User.objects.filter(is_staff=False).count()
    products_count = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()

    # Stock
    out_of_stock = Product.objects.filter(stock=0)
    low_stock = Product.objects.filter(stock__gt=0, stock__lte=LOW_STOCK_THRESHOLD)

    # Ventes des 14 derniers jours (pour un mini graphique).
    days = []
    max_day = Decimal("0")
    for i in range(13, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_orders = paid_orders.filter(created_at__date=day)
        day_total = sum((o.total for o in day_orders), Decimal("0"))
        max_day = max(max_day, day_total)
        days.append({"date": day, "total": day_total, "count": day_orders.count()})
    for d in days:
        d["height"] = int((d["total"] / max_day * 100)) if max_day else 0

    # Répartition par statut.
    status_counts = (
        Order.objects.values("status")
        .annotate(n=Count("id"))
        .order_by("-n")
    )
    status_labels = dict(Order.Status.choices)
    statuses = [
        {"label": status_labels.get(s["status"], s["status"]), "code": s["status"], "n": s["n"]}
        for s in status_counts
    ]

    # Meilleures ventes.
    top_products = (
        OrderItem.objects.values("product_name")
        .annotate(qty=Sum("quantity"), revenue=Sum(F("price") * F("quantity")))
        .order_by("-qty")[:5]
    )

    recent_orders = Order.objects.select_related("user")[:8]

    # --- Aide à la décision ---
    # Meilleurs clients (par total dépensé sur les commandes payées).
    agg = {}
    for o in paid_orders.prefetch_related("items"):
        key = (o.email or o.full_name).lower()
        entry = agg.setdefault(
            key, {"name": o.full_name, "email": o.email, "total": Decimal("0"), "orders": 0}
        )
        entry["total"] += o.total
        entry["orders"] += 1
    top_customers = sorted(agg.values(), key=lambda x: x["total"], reverse=True)[:6]

    # Panier moyen.
    paid_count = paid_orders.count()
    avg_order_value = (revenue / paid_count) if paid_count else Decimal("0")

    # Chiffre d'affaires par catégorie.
    revenue_by_category = (
        OrderItem.objects.filter(order__paid=True, product__isnull=False)
        .values("product__category__name")
        .annotate(
            rev=Coalesce(
                Sum(F("price") * F("quantity"),
                    output_field=DecimalField(max_digits=14, decimal_places=2)),
                Decimal("0"),
            )
        )
        .order_by("-rev")[:8]
    )
    max_cat_rev = max((c["rev"] for c in revenue_by_category), default=Decimal("0"))
    for c in revenue_by_category:
        c["pct"] = int(c["rev"] / max_cat_rev * 100) if max_cat_rev else 0

    # Répartition des moyens de paiement.
    pay_labels = dict(Order.PaymentMethod.choices)
    payment_split = [
        {"label": pay_labels.get(row["payment_method"], row["payment_method"]), "n": row["n"]}
        for row in Order.objects.values("payment_method").annotate(n=Count("id")).order_by("-n")
    ]

    context = {
        "revenue": revenue,
        "revenue_30": revenue_30,
        "orders_total": orders_total,
        "orders_pending": orders_pending,
        "customers": customers,
        "products_count": products_count,
        "active_products": active_products,
        "out_of_stock": out_of_stock,
        "out_of_stock_count": out_of_stock.count(),
        "low_stock": low_stock,
        "low_stock_count": low_stock.count(),
        "days": days,
        "statuses": statuses,
        "top_products": top_products,
        "recent_orders": recent_orders,
        "categories_count": Category.objects.count(),
        "top_customers": top_customers,
        "avg_order_value": avg_order_value,
        "revenue_by_category": revenue_by_category,
        "payment_split": payment_split,
    }
    return render(request, "store/dashboard.html", context)


@superadmin_required
def ai_studio(request):
    """Studio IA (super-admin) : descriptions (Claude) et visuels de marque."""
    result = {}
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "describe":
            name = request.POST.get("name", "").strip()
            if not name:
                flash.error(request, _("Indiquez au moins le nom de l'article."))
            else:
                text, source = ai.generate_description(
                    name=name,
                    category=request.POST.get("category", ""),
                    gender=request.POST.get("gender", ""),
                    keywords=request.POST.get("keywords", ""),
                )
                result = {
                    "description": text,
                    "source": source,
                    "name": name,
                }
                # Attache la description à un article existant si demandé.
                pid = request.POST.get("attach_product")
                if pid:
                    product = get_object_or_404(Product, id=pid)
                    product.description = text
                    product.save(update_fields=["description"])
                    flash.success(
                        request,
                        _("Description enregistrée sur « %(n)s ».") % {"n": product.name},
                    )

        elif action == "image":
            title = request.POST.get("image_title", "DressIT").strip() or "DressIT"
            subtitle = request.POST.get("image_subtitle", "").strip()
            garment = request.POST.get("garment", "tshirt")
            try:
                palette = int(request.POST.get("palette", 0))
            except (TypeError, ValueError):
                palette = 0

            # Photo du modèle fournie par l'admin → visuel de marque à partir d'elle.
            model_photo = request.FILES.get("model_photo")
            if model_photo:
                data = compose_with_photo(model_photo, title, subtitle, palette)
            else:
                data = generate_image(title, subtitle, garment, palette)

            # Sauvegarde un aperçu servable.
            preview_dir = Path(settings.MEDIA_ROOT) / "ai"
            preview_dir.mkdir(parents=True, exist_ok=True)
            fname = f"ai-{uuid.uuid4().hex[:10]}.jpg"
            (preview_dir / fname).write_bytes(data)
            result = {"image_url": f"{settings.MEDIA_URL}ai/{fname}"}

            # Attache le visuel à un article existant si demandé.
            pid = request.POST.get("attach_product")
            if pid:
                product = get_object_or_404(Product, id=pid)
                img = ProductImage(product=product, alt=title)
                img.image.save(f"ai-{product.slug}-{fname}", ContentFile(data), save=True)
                flash.success(
                    request,
                    _("Visuel ajouté aux photos de « %(n)s ».") % {"n": product.name},
                )

    context = {
        "result": result,
        "ai_available": ai.ai_available(),
        "ai_model": ai.DEFAULT_MODEL,
        "products": Product.objects.order_by("name"),
        "categories": Category.objects.all(),
        "garments": sorted(GARMENTS.keys()),
    }
    return render(request, "store/ai_studio.html", context)
