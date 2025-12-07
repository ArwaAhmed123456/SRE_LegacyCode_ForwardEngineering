from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from pos_app.models import Employee, Category, Supplier, Product

class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data...')

        # Create dummy employees
        employees_data = [
            {
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@pos.com',
                'role': 'ADMIN',
                'password': 'admin123'
            },
            {
                'username': 'manager',
                'first_name': 'Manager',
                'last_name': 'User',
                'email': 'manager@pos.com',
                'role': 'MANAGER',
                'password': 'manager123'
            },
            {
                'username': 'cashier',
                'first_name': 'Cashier',
                'last_name': 'User',
                'email': 'cashier@pos.com',
                'role': 'CASHIER',
                'password': 'cashier123'
            },
            {
                'username': 'employee',
                'first_name': 'Tom',
                'last_name': 'Employee',
                'email': 'employee@pos.com',
                'role': 'EMPLOYEE',
                'password': 'employee123'
            },
            {
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@pos.com',
                'role': 'CASHIER',
                'password': 'password123'
            },
            {
                'username': 'jane_smith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@pos.com',
                'role': 'MANAGER',
                'password': 'password123'
            },
            {
                'username': 'bob_johnson',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'email': 'bob.johnson@pos.com',
                'role': 'EMPLOYEE',
                'password': 'password123'
            }
        ]

        for emp_data in employees_data:
            employee, created = Employee.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'email': emp_data['email'],
                    'role': emp_data['role'],
                    'password': make_password(emp_data['password']),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created employee: {employee.get_full_name()}')
            else:
                self.stdout.write(f'Employee already exists: {employee.get_full_name()}')

        # Create dummy categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Books', 'description': 'Books and publications'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'description': 'Sports equipment and apparel'}
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create dummy suppliers
        suppliers_data = [
            {'name': 'TechCorp', 'email': 'contact@techcorp.com', 'phone': '555-0101'},
            {'name': 'FashionHub', 'email': 'info@fashionhub.com', 'phone': '555-0102'},
            {'name': 'BookWorld', 'email': 'orders@bookworld.com', 'phone': '555-0103'},
            {'name': 'HomeDepot', 'email': 'support@homedepot.com', 'phone': '555-0104'},
            {'name': 'SportsPro', 'email': 'sales@sportspro.com', 'phone': '555-0105'}
        ]

        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults={
                    'email': sup_data['email'],
                    'phone': sup_data['phone']
                }
            )
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

        # Create dummy products
        products_data = [
            {'name': 'Laptop', 'sku': 'LAP001', 'price': Decimal('999.99'), 'quantity': 10, 'min_stock_level': 2, 'category_name': 'Electronics', 'supplier_name': 'TechCorp'},
            {'name': 'Smartphone', 'sku': 'SPH001', 'price': Decimal('599.99'), 'quantity': 15, 'min_stock_level': 3, 'category_name': 'Electronics', 'supplier_name': 'TechCorp'},
            {'name': 'T-Shirt', 'sku': 'TSH001', 'price': Decimal('19.99'), 'quantity': 50, 'min_stock_level': 10, 'category_name': 'Clothing', 'supplier_name': 'FashionHub'},
            {'name': 'Jeans', 'sku': 'JEA001', 'price': Decimal('49.99'), 'quantity': 30, 'min_stock_level': 5, 'category_name': 'Clothing', 'supplier_name': 'FashionHub'},
            {'name': 'Python Programming Book', 'sku': 'BOO001', 'price': Decimal('39.99'), 'quantity': 20, 'min_stock_level': 5, 'category_name': 'Books', 'supplier_name': 'BookWorld'},
            {'name': 'Garden Hose', 'sku': 'HOS001', 'price': Decimal('29.99'), 'quantity': 25, 'min_stock_level': 5, 'category_name': 'Home & Garden', 'supplier_name': 'HomeDepot'},
            {'name': 'Basketball', 'sku': 'BAL001', 'price': Decimal('24.99'), 'quantity': 40, 'min_stock_level': 8, 'category_name': 'Sports', 'supplier_name': 'SportsPro'},
            {'name': 'Running Shoes', 'sku': 'SHO001', 'price': Decimal('89.99'), 'quantity': 20, 'min_stock_level': 4, 'category_name': 'Sports', 'supplier_name': 'SportsPro'}
        ]

        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category_name'])
            supplier = Supplier.objects.get(name=prod_data['supplier_name'])

            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'price': prod_data['price'],
                    'quantity': prod_data['quantity'],
                    'min_stock_level': prod_data['min_stock_level'],
                    'category': category,
                    'supplier': supplier,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Dummy data creation completed!'))
