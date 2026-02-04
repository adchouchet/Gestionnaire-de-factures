from django.contrib import admin
from .models import Product, Invoice, InvoiceItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_price', 'stock_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'date', 'total_amount', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['invoice_number']
    readonly_fields = ['invoice_number', 'total_amount']
    ordering = ['-date', '-created_at']
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'product', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['invoice__date']
    readonly_fields = ['subtotal']
