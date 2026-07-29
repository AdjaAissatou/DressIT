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
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Count, F, Sum
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext as _

from . import ai
from .models import Category, Order, OrderItem, Product, ProductImage
from .placeholder_images import GARMENTS, generate_image

LOW_STOCK_THRESHOLD = 5


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
    }
    return render(request, "store/dashboard.html", context)


@staff_member_required
def ai_studio(request):
    """Studio IA : génère des descriptions (Claude) et des visuels de marque."""
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
