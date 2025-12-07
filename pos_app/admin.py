from django.contrib import admin
from .models import (
    Employee,
    Category,
    Supplier,
    Product,
    Customer,
    Coupon,
    Sale,
    SaleItem,
    Rental,
    RentalItem,
    RentalPayment,
    Payment,
    OfflineTransaction,
    StockMovement,
)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'quantity', 'min_stock_level', 'category', 'supplier', 'is_active')
    list_filter = ('category', 'supplier', 'is_active')
    search_fields = ('name', 'sku', 'description')
    ordering = ('name',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'movement_type', 'employee', 'timestamp')
    list_filter = ('movement_type',)
    search_fields = ('product__name', 'employee__username')
    ordering = ('-timestamp',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'created_at', 'quantity_change')
    list_filter = ('created_at', 'customer', 'state')
    ordering = ('-created_at',)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price')
    search_fields = ('product__name',)
    ordering = ('sale',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    # Use model fields and @property in list_display
    list_display = ('id', 'customer', 'due_date', 'total', 'created_at', 'quantity_change')
    list_filter = ('due_date', 'customer')
    ordering = ('due_date',)


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('rental', 'product', 'quantity')
    search_fields = ('product__name',)
    ordering = ('rental',)


@admin.register(RentalPayment)
class RentalPaymentAdmin(admin.ModelAdmin):
    list_display = ('rental', 'amount', 'payment_method', 'transaction_id')
    list_filter = ('payment_method',)
    ordering = ('-id',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'expires_at')
    list_filter = ('is_active',)
    search_fields = ('code',)
    ordering = ('code',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'is_active')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'payment_method', 'transaction_id', 'paid_at')
    list_filter = ('payment_method',)
    ordering = ('-paid_at',)


@admin.register(OfflineTransaction)
class OfflineTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'reference_number', 'amount', 'transaction_date')
    ordering = ('-transaction_date',)
