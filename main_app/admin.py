# admin.py
from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'serial_number', 'sale_price', 'unit_price', 'updated_at')
    list_filter = ('type', 'updated_at')
    search_fields = ('name', 'serial_number')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'discount', 'final_price', 'profit', 'created_at')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_price', 'total_profit', 'order_date')
    inlines = [OrderItemInline]
    search_fields = ('customer_name', 'customer_phone', 'id')
