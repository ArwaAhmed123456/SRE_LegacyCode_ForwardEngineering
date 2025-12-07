from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from pos_app.models import Product, Employee, Sale, SaleItem

User = get_user_model()

class InventorySignalTest(TestCase):
    def setUp(self):
        # Create employee
        self.employee = User.objects.create_user(
            username='testuser', password='testpass',
            role='CASHIER'
        )

        # Create product with stock
        self.product = Product.objects.create(
            name='Test Product',
            sku='TP001',
            price=Decimal('10.00'),
            quantity=20,
            min_stock_level=5,
            category=None,  # Assign a valid category if required
            supplier=None,  # Assign a valid supplier if required
            is_active=True
        )

        # Create sale
        self.sale = Sale.objects.create(
            employee=self.employee,
            total=Decimal('0.00')
        )

    def test_saleitem_creation_reduces_stock(self):
        initial_quantity = self.product.quantity
        quantity_sold = 3

        sale_item = SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=quantity_sold,
            price=self.product.price
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, initial_quantity - quantity_sold)
