"""Sérialiseurs de l'API REST DressIT."""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from store.models import (
    Category,
    Color,
    Complaint,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Size,
)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "hex_code"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "label"]


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "url", "alt"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "gender", "description"]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    image = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "category", "gender", "price",
            "compare_at_price", "is_on_sale", "discount_percent", "in_stock",
            "image", "colors",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        img = obj.main_image
        if img and request:
            return request.build_absolute_uri(img.url)
        return img.url if img else None


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    stock = serializers.IntegerField(read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description", "images", "sizes", "stock"]


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "price", "quantity", "size", "color", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "full_name", "email", "phone", "address", "city", "postal_code",
            "country", "note", "payment_method", "payment_method_display",
            "status", "status_display", "paid", "shipping_cost", "discount",
            "promo_code", "subtotal", "total", "items", "created_at",
        ]


class ComplaintSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source="get_subject_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id", "name", "email", "phone", "subject", "subject_display",
            "order", "message", "status", "status_display", "response", "created_at",
        ]
        read_only_fields = ["status", "response", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            password=validated_data["password"],
        )
