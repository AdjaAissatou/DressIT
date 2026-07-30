"""Vues de l'API REST DressIT (consommée par l'application mobile)."""

from decimal import Decimal

from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from store import imagesearch, payments
from store.emails import send_complaint_received, send_order_confirmation
from store.models import Category, Favorite, Gender, Order, OrderItem, Product, PromoCode

from .serializers import (
    CategorySerializer,
    ComplaintSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    RegisterSerializer,
    UserSerializer,
)


# --------------------------------------------------------------------------- #
# Authentification
# --------------------------------------------------------------------------- #
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate

    user = authenticate(
        username=request.data.get("username"), password=request.data.get("password")
    )
    if not user:
        return Response({"detail": "Identifiants invalides."}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": UserSerializer(user).data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #
class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None


class ProductList(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.available().prefetch_related("images", "colors")
        p = self.request.query_params
        gender = p.get("gender")
        if gender == Gender.HOMME:
            qs = qs.filter(gender__in=[Gender.HOMME, Gender.UNISEXE])
        elif gender == Gender.FEMME:
            qs = qs.filter(gender__in=[Gender.FEMME, Gender.UNISEXE])
        if p.get("category"):
            qs = qs.filter(category__slug=p["category"])
        if p.get("q"):
            qs = qs.filter(Q(name__icontains=p["q"]) | Q(description__icontains=p["q"]))
        sort = {
            "recent": "-created_at", "price_asc": "price",
            "price_desc": "-price", "name": "name",
        }.get(p.get("sort", "recent"), "-created_at")
        return qs.order_by(sort)


class ProductDetail(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    queryset = Product.objects.available().prefetch_related("images", "sizes", "colors")


class PhotoSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        photo = request.FILES.get("photo")
        if not photo:
            return Response({"detail": "Aucune photo fournie."}, status=400)
        matches = imagesearch.search(photo)
        products = [p for p, _d in matches]
        data = ProductListSerializer(products, many=True, context={"request": request}).data
        return Response({"results": data})


# --------------------------------------------------------------------------- #
# Favoris
# --------------------------------------------------------------------------- #
class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.available().filter(favorited_by__user=request.user)
        data = ProductListSerializer(products, many=True, context={"request": request}).data
        return Response({"results": data})

    def post(self, request):
        product = Product.objects.filter(id=request.data.get("product_id")).first()
        if not product:
            return Response({"detail": "Article introuvable."}, status=404)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            fav.delete()
        return Response({"added": created})


# --------------------------------------------------------------------------- #
# Code promo
# --------------------------------------------------------------------------- #
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def promo_validate(request):
    code = (request.data.get("code") or "").strip().upper()
    subtotal = Decimal(str(request.data.get("subtotal", "0")))
    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return Response({"valid": False, "message": "Code promo invalide."})
    valid, msg = promo.check_validity(subtotal)
    if not valid:
        return Response({"valid": False, "message": msg})
    return Response({
        "valid": True,
        "code": promo.code,
        "discount": str(promo.compute_discount(subtotal)),
    })


# --------------------------------------------------------------------------- #
# Commandes & paiement
# --------------------------------------------------------------------------- #
def _shipping_for(subtotal, discount):
    threshold = Decimal(str(settings.DRESSIT_FREE_SHIPPING_THRESHOLD))
    fee = Decimal(str(settings.DRESSIT_SHIPPING_FEE))
    return Decimal("0") if (subtotal - discount) >= threshold else fee


class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        items = request.data.get("items") or []
        if not items:
            return Response({"detail": "Panier vide."}, status=400)

        method = request.data.get("payment_method", Order.PaymentMethod.WAVE)
        if method == Order.PaymentMethod.WAVE and not payments.wave_enabled():
            return Response({"detail": "Wave non configuré."}, status=400)
        if method == Order.PaymentMethod.ORANGE_MONEY and not payments.om_enabled():
            return Response({"detail": "Orange Money non configuré."}, status=400)

        # Reconstitue les lignes avec les prix RÉELS côté serveur.
        lines, subtotal = [], Decimal("0")
        for it in items:
            product = Product.objects.available().filter(id=it.get("product_id")).first()
            if not product:
                continue
            qty = max(1, int(it.get("quantity", 1)))
            lines.append((product, qty, it.get("size", ""), it.get("color", "")))
            subtotal += product.price * qty
        if not lines:
            return Response({"detail": "Aucun article valide."}, status=400)

        # Code promo (optionnel).
        discount = Decimal("0")
        promo = None
        code = (request.data.get("promo_code") or "").strip().upper()
        if code:
            promo = PromoCode.objects.filter(code=code).first()
            if promo:
                ok, _msg = promo.check_validity(subtotal)
                discount = promo.compute_discount(subtotal) if ok else Decimal("0")
                if not ok:
                    promo = None

        shipping = _shipping_for(subtotal, discount)

        order = Order.objects.create(
            user=request.user,
            full_name=request.data.get("full_name", ""),
            email=request.data.get("email", request.user.email),
            phone=request.data.get("phone", ""),
            address=request.data.get("address", ""),
            city=request.data.get("city", ""),
            postal_code=request.data.get("postal_code", ""),
            country=request.data.get("country", "Sénégal"),
            note=request.data.get("note", ""),
            payment_method=method,
            shipping_cost=shipping,
            discount=discount,
            promo_code=promo.code if promo else "",
            status=Order.Status.PENDING,
        )
        for product, qty, size, color in lines:
            OrderItem.objects.create(
                order=order, product=product, product_name=product.name,
                price=product.price, quantity=qty, size=size, color=color,
            )
        if promo:
            promo.used_count += 1
            promo.save(update_fields=["used_count"])

        payment_url = None
        if method == Order.PaymentMethod.COD:
            from store.views import _commit_stock

            _commit_stock(order)
            send_order_confirmation(order, request)
        else:
            try:
                if method == Order.PaymentMethod.WAVE:
                    payment_url = payments.wave_create_session(order, request)
                else:
                    payment_url = payments.om_create_payment(order, request)
            except payments.PaymentError as exc:
                order.delete()
                return Response({"detail": f"Paiement impossible : {exc}"}, status=400)

        data = OrderSerializer(order, context={"request": request}).data
        data["payment_url"] = payment_url
        return Response(data, status=201)


class OrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders.prefetch_related("items").all()


class OrderDetail(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders.prefetch_related("items").all()


# --------------------------------------------------------------------------- #
# Réclamations
# --------------------------------------------------------------------------- #
class ComplaintListCreate(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer

    def get_permissions(self):
        # Créer une réclamation est ouvert ; lister demande d'être connecté.
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.complaints.all()
        return self.request.user.complaints.none() if hasattr(self.request.user, "complaints") else []

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        complaint = serializer.save(user=user)
        send_complaint_received(complaint, self.request)


# --------------------------------------------------------------------------- #
# Configuration de la boutique (devise, livraison, passerelles…)
# --------------------------------------------------------------------------- #
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def config_view(request):
    return Response({
        "currency": settings.DRESSIT_CURRENCY_SYMBOL,
        "shipping_fee": str(settings.DRESSIT_SHIPPING_FEE),
        "free_shipping_threshold": str(settings.DRESSIT_FREE_SHIPPING_THRESHOLD),
        "payment_methods": {
            "wave": payments.wave_enabled(),
            "orange_money": payments.om_enabled(),
            "cod": True,
        },
        "languages": [code for code, _ in settings.LANGUAGES],
    })
