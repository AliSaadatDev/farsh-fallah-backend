from rest_framework import serializers
from persiantools.jdatetime import JalaliDateTime
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import CARPET_BRANCHES, TABLEAU_BRANCHES
from .models import Product, Order, OrderItem
from .image_utils import process_image
from django.db.models import Sum


class JalaliDateTimeField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return None
        j = JalaliDateTime.to_jalali(value)
        return j.strftime("%Y/%m/%d - %H:%M")

    def to_internal_value(self, data):
        try:
            return JalaliDateTime.strptime(data, "%Y/%m/%d - %H:%M").to_datetime()
        except Exception:
            raise serializers.ValidationError("فرمت تاریخ شمسی معتبر نیست.")


class ProductSerializer(serializers.ModelSerializer):
    created_at = JalaliDateTimeField(read_only=True)
    updated_at = JalaliDateTimeField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "type", "branch", "serial_number", "name", "description",
            "unit_price", "sale_price", "image", "length", "width", "size", "crop_sex",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        image = validated_data.get("image")
        if image:
            validated_data["image"] = process_image(image, size=(300, 500), target_kb=100)

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        image = validated_data.get("image")
        if image:
            validated_data["image"] = process_image(image, size=(300, 500), target_kb=100)

        return super().update(instance, validated_data)

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative")
        return value

    def validate_sale_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Sale price cannot be negative")
        return value

    def validate(self, data):

        product_type = data.get("type")
        branch = data.get("branch")

        size = data.get("size")
        length = data.get("length")
        width = data.get("width")

        if product_type == "carpet":
            valid = [b[0] for b in CARPET_BRANCHES]
            if branch not in valid:
                raise serializers.ValidationError("این شاخه متعلق به نوع 'فرش' نیست.")

        elif product_type == "tableau":
            valid = [b[0] for b in TABLEAU_BRANCHES]
            if branch not in valid:
                raise serializers.ValidationError("این شاخه متعلق به نوع 'تابلوفرش' نیست.")

        if product_type == "carpet":
            if not size:
                raise serializers.ValidationError("برای فرش وارد کردن size الزامی است.")
            if length or width:
                raise serializers.ValidationError("برای فرش نباید length یا width وارد کنید.")

        elif product_type == "tableau":
            if not length or not width:
                raise serializers.ValidationError("برای تابلوفرش وارد کردن length و width الزامی است.")
            if size:
                raise serializers.ValidationError("برای تابلوفرش نباید size وارد کنید.")

        return data




class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='product', queryset=Product.objects.all()
    )
    created_at = JalaliDateTimeField(read_only=True)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=Decimal('0.00'))
    discount_percent = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def get_discount_percent(self, obj):
        if obj.price > 0:
            percent = (obj.discount / obj.price) * 100
            return round(percent, 2)
        return 0

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "price", "discount", "discount_percent", "final_price", "profit", "created_at"]
        read_only_fields = ["id", "product", "final_price", "profit", "created_at", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_date = JalaliDateTimeField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer_name", "customer_phone", "customer_city", "customer_state", "customer_region", "customer_address", "total_price", "total_profit", "order_date", "items"]
        read_only_fields = ["id", "order_date", "total_price", "total_profit"]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer_name", "customer_phone", "customer_city", "customer_state", "customer_region", "customer_address", "items"]
        read_only_fields = ["id"]

    def validate_items(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("items must be a non-empty list of {'product': id, 'discount': optional}")
        for entry in value:
            if 'product' not in entry:
                raise serializers.ValidationError("each item must contain 'product' id")
            disc = entry.get('discount', 0)
            try:
                d = Decimal(str(disc))
            except Exception:
                raise serializers.ValidationError("discount must be a number")
            if d < Decimal('0.00'):
                raise serializers.ValidationError("discount cannot be negative")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in items_data:
                product = get_object_or_404(Product, pk=item['product'])

                price = product.sale_price if product.sale_price is not None else product.unit_price

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=price,
                    discount=Decimal(str(item.get('discount', '0')))
                )
            totals = order.items.aggregate(
                total_price=Sum('final_price'),
                total_profit=Sum('profit')
            )

            order.total_price = totals['total_price'] or Decimal('0.00')
            order.total_profit = totals['total_profit'] or Decimal('0.00')
            order.save(update_fields=['total_price', 'total_profit'])

        return order
