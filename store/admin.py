"""Interface d'administration : gérer articles, photos et commandes facilement."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .templatetags.store_extras import money

from .emails import send_complaint_response
from .models import (
    Category,
    Color,
    Complaint,
    Favorite,
    Order,
    OrderItem,
    Product,
    ProductImage,
    PromoCode,
    Size,
)

admin.site.site_header = "DressIT — Administration"
admin.site.site_title = "DressIT"
admin.site.index_title = _("Gestion de la boutique")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # 3 champs photo vides prêts à l'emploi
    fields = ("preview", "image", "alt", "order")
    readonly_fields = ("preview",)

    @admin.display(description=_("Aperçu"))
    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:8px;object-fit:cover;" />',
                obj.image.url,
            )
        return "—"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "name",
        "category",
        "gender",
        "price",
        "stock",
        "is_active",
        "is_featured",
    )
    list_display_links = ("thumbnail", "name")
    list_editable = ("price", "stock", "is_active", "is_featured")
    list_filter = ("gender", "category", "is_active", "is_featured")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("sizes", "colors")
    inlines = [ProductImageInline]
    autocomplete_fields = ("category",)
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "gender", "description")}),
        (_("Prix & promotion"), {"fields": ("price", "compare_at_price")}),
        (_("Variantes"), {"fields": ("sizes", "colors", "stock")}),
        (_("Visibilité"), {"fields": ("is_active", "is_featured")}),
    )

    @admin.display(description="")
    def thumbnail(self, obj):
        img = obj.main_image
        if img:
            return format_html(
                '<img src="{}" style="height:44px;width:44px;border-radius:8px;object-fit:cover;" />',
                img.url,
            )
        return "—"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "gender", "order")
    list_editable = ("order",)
    list_filter = ("gender",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("label", "order")
    list_editable = ("order",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("swatch", "name", "hex_code")
    search_fields = ("name",)

    @admin.display(description=_("Couleur"))
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;height:20px;width:20px;border-radius:50%;'
            'border:1px solid #999;background:{};"></span>',
            obj.hex_code,
        )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "price",
        "quantity",
        "size",
        "color",
        "subtotal",
    )
    can_delete = False

    @admin.display(description=_("Sous-total"))
    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "total_display",
        "payment_method",
        "status",
        "paid",
        "created_at",
    )
    list_filter = ("status", "paid", "payment_method", "created_at")
    search_fields = ("full_name", "email", "phone", "id")
    readonly_fields = ("created_at", "updated_at", "total_display")
    inlines = [OrderItemInline]
    list_editable = ("status", "paid")
    date_hierarchy = "created_at"
    fieldsets = (
        (_("Client"), {"fields": ("user", "full_name", "email", "phone")}),
        (_("Livraison"), {"fields": ("address", "city", "postal_code", "country", "note")}),
        (
            _("Paiement & statut"),
            {"fields": ("payment_method", "paid", "status", "total_display")},
        ),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("Total"))
    def total_display(self, obj):
        return money(obj.total)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "min_subtotal",
        "active",
        "valid_until",
        "used_count",
        "max_uses",
    )
    list_editable = ("active",)
    list_filter = ("active", "discount_type")
    search_fields = ("code",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
    autocomplete_fields = ("user", "product")


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subject", "status", "order", "created_at")
    list_filter = ("status", "subject", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "email", "message", "id")
    readonly_fields = ("name", "email", "phone", "subject", "order", "message", "created_at")
    date_hierarchy = "created_at"
    fieldsets = (
        (_("Réclamation"), {"fields": ("name", "email", "phone", "subject", "order", "message", "created_at")}),
        (_("Traitement"), {"fields": ("status", "response")}),
    )

    def save_model(self, request, obj, form, change):
        # Envoie la réponse au client si elle vient d'être saisie/modifiée.
        send_response = False
        if change and "response" in form.changed_data and obj.response.strip():
            send_response = True
        super().save_model(request, obj, form, change)
        if send_response:
            send_complaint_response(obj, request)
            self.message_user(request, _("Réponse envoyée au client par e-mail."))
