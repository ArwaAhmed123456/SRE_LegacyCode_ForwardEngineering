from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from decimal import Decimal

from .models import (
    Employee, Product, Category, Supplier, Sale, SaleItem, Payment,
    Coupon, Customer, Rental, RentalItem, StockMovement
)
from .forms import (
    ProductForm, CategoryForm, SupplierForm, SaleForm, SaleItemForm,
    CouponForm, CustomerForm, RentalForm, RentalItemForm, EmployeeRegistrationForm, PaymentForm, OfflineTransactionForm
)

# Dashboard view
@login_required
def dashboard(request):
    """Main dashboard view."""
    context = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'low_stock_products': Product.objects.filter(quantity__lte=F('min_stock_level'), is_active=True).count(),
        'total_sales': Sale.objects.filter(sale_status='COMPLETED').count(),
        'total_sales_value': Sale.objects.filter(sale_status='COMPLETED').annotate(
            total=Sum(ExpressionWrapper(
                F('items__product__price') * F('items__quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        ).aggregate(total=Sum('total'))['total'] or 0,
        'active_rentals': Rental.objects.filter(rental_status='ACTIVE').count(),
        'overdue_rentals': Rental.objects.filter(rental_status='OVERDUE').count(),
        'recent_sales': Sale.objects.filter(sale_status='COMPLETED').order_by('-date')[:5],
        'recent_rentals': Rental.objects.filter(rental_status='ACTIVE').order_by('-date')[:5],
    }
    return render(request, 'dashboard.html', context)

# Cashier view
@login_required
def cashier(request):
    """Cashier interface with cart functionality."""
    cart = request.session.get('cart', {})
    products = Product.objects.filter(is_active=True)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_to_cart':
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))

            if product_id in cart:
                cart[product_id]['quantity'] += quantity
            else:
                product = get_object_or_404(Product, pk=product_id)
                cart[product_id] = {
                    'name': product.name,
                    'price': str(product.price),
                    'quantity': quantity,
                    'sku': product.sku
                }

        elif action == 'remove_from_cart':
            product_id = request.POST.get('product_id')
            if product_id in cart:
                del cart[product_id]

        elif action == 'update_quantity':
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            if product_id in cart:
                cart[product_id]['quantity'] = quantity

        elif action == 'checkout':
            return redirect('checkout')

        request.session['cart'] = cart
        return redirect('cashier')

    # Calculate cart totals
    cart_items = []
    subtotal = 0
    for product_id, item in cart.items():
        product = Product.objects.get(pk=product_id)
        quantity = item['quantity']
        price = Decimal(item['price'])
        total = price * quantity
        subtotal += total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'total': total
        })

    tax_rate = Decimal('0.06')  # Default tax rate
    tax = subtotal * tax_rate
    total = subtotal + tax

    context = {
        'products': products,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    return render(request, 'cashier.html', context)

# Checkout view
@login_required
def checkout(request):
    """Checkout process."""
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('cashier')

    if request.method == 'POST':
        # Create sale
        sale = Sale.objects.create(
            employee=request.user,
            created_by=request.user
        )

        # Add items to sale
        for product_id, item in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            quantity = item['quantity']
            price = Decimal(item['price'])

            sale.add_item(product, quantity, price)

        # Clear cart
        request.session['cart'] = {}

        messages.success(request, f"Sale #{sale.invoice_number} created successfully!")
        return redirect('sale_detail', pk=sale.pk)

    # Calculate totals for display
    cart_items = []
    subtotal = Decimal('0.00')
    total_items = 0

    for product_id, item_data in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        quantity = item_data['quantity']
        item_total = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': product.price,
            'total': item_total,
        })

        subtotal += item_total
        total_items += quantity

    context = {
        'products': Product.objects.filter(is_active=True),
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'checkout.html', context)

# Product CRUD views
@login_required
def product_list(request):
    if request.user.role != 'admin':
        return redirect('home')
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.user.role != 'admin':
        return redirect('home')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully")
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

# Sale views
@login_required
def sale_list(request):
    if request.user.role != 'admin':
        return redirect('home')
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'sale_list.html', {'sales': sales})

@login_required
def sale_detail(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    sale = get_object_or_404(Sale, pk=pk)
    items = SaleItem.objects.filter(sale=sale)
    return render(request, 'sale_detail.html', {'sale': sale, 'items': items})

# Reports view
@login_required
def reports(request):
    if request.user.role != 'admin':
        return redirect('home')
    total_sales = Sale.objects.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(total=Sum('total'))['total'] or 0
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(quantity__lte=10)
    recent_sales = Sale.objects.filter(date__gte=timezone.now() - timezone.timedelta(days=30))
    total_profit = sum(sale.get_profit() for sale in Sale.objects.all())
    return render(request, 'reports.html', {
        'total_sales': total_sales,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'total_profit': total_profit
    })

@login_required
def dashboard_view(request):
    """Main dashboard - equivalent to legacy POSApplication main screen."""
    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)

    # Sales Statistics
    today_sales = Sale.objects.filter(
        date__date=today,
        sale_status=Sale.SaleStatus.COMPLETED
    )
    today_total = today_sales.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(total=Sum('total'))['total'] or 0
    today_count = today_sales.count()

    month_sales = Sale.objects.filter(
        date__date__gte=today.replace(day=1),
        sale_status=Sale.SaleStatus.COMPLETED
    )
    month_total = month_sales.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(total=Sum('total'))['total'] or 0

    # Inventory Statistics
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(
        quantity__lte=F('min_stock_level')
    ).count()
    out_of_stock_count = Product.objects.filter(quantity=0).count()

    # Employee Statistics (since no customers in model)
    total_employees = Employee.objects.count()

    # Recent Sales
    recent_sales = Sale.objects.filter(
        sale_status=Sale.SaleStatus.COMPLETED
    ).order_by('-date')[:10]

    # Low Stock Products
    low_stock_products = Product.objects.filter(
        quantity__lte=F('min_stock_level')
    ).order_by('quantity')[:5]

    # Top Selling Products (last 30 days)
    top_products = SaleItem.objects.filter(
        sale__date__date__gte=thirty_days_ago,
        sale__sale_status=Sale.SaleStatus.COMPLETED
    ).values(
        'product__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('unit_price') * Sum('quantity')
    ).order_by('-quantity_sold')[:5]

    # Daily Sales for Chart
    daily_sales_data = []
    for i in range(6, -1, -1):
        date = today - timezone.timedelta(days=i)
        daily_sales = Sale.objects.filter(
            date__date=date,
            sale_status=Sale.SaleStatus.COMPLETED
        ).annotate(
            total=Sum(ExpressionWrapper(
                F('items__product__price') * F('items__quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        ).aggregate(
            total=Sum('total'),
            count=Count('id')
        )

        daily_sales_data.append({
            'date': date.strftime('%b %d'),
            'total': daily_sales['total'] or 0,
            'count': daily_sales['count'] or 0
        })

    context = {
        'today_total': today_total,
        'today_count': today_count,
        'month_total': month_total,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_customers': total_employees,  # Using employees as customers for now
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        'daily_sales_data': daily_sales_data,
    }

    return render(request, 'dashboard.html', context)


# Product Management Views
class ProductListView(LoginRequiredMixin, ListView):
    """Product list view - equivalent to legacy product management."""
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'supplier')

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        # Filters
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category__id=category)

        low_stock = self.request.GET.get('low_stock', '')
        if low_stock:
            queryset = queryset.filter(quantity__lte=F('min_stock_level'))

        out_of_stock = self.request.GET.get('out_of_stock', '')
        if out_of_stock:
            queryset = queryset.filter(quantity=0)

        active_only = self.request.GET.get('active_only', 'true')
        if active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)

        # Sorting
        sort = self.request.GET.get('sort', 'name')
        order = self.request.GET.get('order', 'asc')
        if sort and hasattr(Product, sort):
            if order == 'desc':
                sort = f'-{sort}'
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_value'] = Product.objects.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0
        context['low_stock_count'] = Product.objects.filter(
            quantity__lte=F('min_stock_level'),
            is_active=True
        ).count()
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Product "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'

    def get_success_url(self):
        messages.success(self.request, "Product updated successfully!")
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, f'Product "{product.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ProductDetailView(LoginRequiredMixin, DetailView):
    """Product detail view."""
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_movements'] = StockMovement.objects.filter(
            product=self.object
        ).order_by('-created_at')[:20]
        return context

@login_required
def update_stock_view(request, pk):
    """Update stock view - legacy inventory update functionality."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        quantity_change = int(request.POST.get('quantity_change', 0))
        movement_type = request.POST.get('movement_type', 'ADJUSTMENT')
        notes = request.POST.get('notes', '')

        try:
            product.update_stock(quantity_change, movement_type, request.user.employee, notes)
            messages.success(request, f"Stock updated successfully! New quantity: {product.quantity}")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('product_detail', pk=product.pk)

    return render(request, 'update_stock.html', {'product': product})

# Category Management Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        queryset = Category.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Supplier Management Views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        queryset = Supplier.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

    def delete(self, request, *args, **kwargs):
        supplier = self.get_object()
        messages.success(request, f'Supplier "{supplier.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Employee Management Views
class EmployeeListView(LoginRequiredMixin, ListView):
    """Employee list view for admin."""
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.all().order_by('first_name', 'last_name')

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )

        # Role filter
        role = self.request.GET.get('role', '')
        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Employee.Role.choices
        return context

# Sales Processing Views (Legacy Sale Processing)
class SaleListView(LoginRequiredMixin, ListView):
    """Sale list view - equivalent to legacy sale history."""
    model = Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee', 'created_by')

        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(employee__first_name__icontains=search) |
                Q(employee__last_name__icontains=search) |
                Q(employee__username__icontains=search)
            )

        # Date filter
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        if start_date:
            queryset = queryset.filter(date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__date__lte=end_date)

        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(sale_status=status)

        # Payment status filter
        payment_status = self.request.GET.get('payment_status', '')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        # Sorting
        queryset = queryset.order_by('-date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sales'] = Sale.objects.filter(
            sale_status=Sale.SaleStatus.COMPLETED
        ).annotate(
            total=Sum(ExpressionWrapper(
                F('items__product__price') * F('items__quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        ).aggregate(total=Sum('total'))['total'] or 0
        context['total_count'] = Sale.objects.count()
        return context

class SaleCreateView(LoginRequiredMixin, CreateView):
    """Create sale view - equivalent to legacy sale processing."""
    model = Sale
    form_class = SaleForm
    template_name = 'cashier.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.employee = self.request.user.employee
        form.instance.sale_status = Sale.SaleStatus.PENDING

        # Save the sale first
        sale = form.save()

        # Add items from session/cart
        cart = self.request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(pk=product_id, is_active=True)
                sale.add_item(product, quantity)
            except (Product.DoesNotExist, ValidationError) as e:
                messages.warning(self.request, str(e))

        # Clear cart
        if 'cart' in self.request.session:
            del self.request.session['cart']

        messages.success(self.request, f"Sale created successfully! Invoice #{sale.invoice_number}")
        return redirect('sale_detail', pk=sale.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True, quantity__gt=0)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = 0
        for product_id, qty in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                subtotal = product.price * qty
                total += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'subtotal': subtotal
                })
            except Product.DoesNotExist:
                pass  # Skip invalid products
        context['cart_items'] = cart_items
        context['total'] = total
        return context

class SaleDetailView(LoginRequiredMixin, DetailView):
    """Sale detail view."""
    model = Sale
    template_name = 'sale_detail.html'
    context_object_name = 'sale'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = Payment.objects.filter(sale=self.object)
        return context

@login_required
@require_POST
def add_to_cart_view(request):
    """Add product to cart - AJAX endpoint."""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(pk=product_id, is_active=True)

        if product.quantity < quantity:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.quantity} units available'
            })

        cart = request.session.get('cart', {})
        current_qty = cart.get(str(product_id), 0)
        cart[str(product_id)] = current_qty + quantity
        request.session['cart'] = cart

        return JsonResponse({
            'success': True,
            'cart_total': sum(cart.values()),
            'product_name': product.name
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})

@login_required
def process_payment_view(request, pk):
    """Process payment for sale."""
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                sale.process_payment(
                    amount=form.cleaned_data['amount'],
                    payment_method=form.cleaned_data['payment_method'],
                    transaction_id=form.cleaned_data['transaction_id'],
                    notes=form.cleaned_data['notes']
                )
                messages.success(request, f"Payment of ${form.cleaned_data['amount']} processed successfully!")
            except ValidationError as e:
                messages.error(request, str(e))

            return redirect('sale_detail', pk=sale.pk)
    else:
        form = PaymentForm(initial={'amount': sale.balance_due})

    return render(request, 'sale_detail.html', {
        'sale': sale,
        'form': form
    })

# Authentication Views
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse

def login_view(request):
    """Login view."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

class EmployeeRegistrationView(CreateView):
    model = Employee
    form_class = EmployeeRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.get_full_name()}! Your account has been created.')
        return super().form_valid(form)

@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'profile.html', {'user': request.user})

@login_required
def home_view(request):
    """Home view - redirects to appropriate dashboard."""
    if request.user.role == 'admin':
        return redirect('dashboard')
    else:
        return redirect('cashier')

@login_required
def cashier_view(request):
    """Cashier interface."""
    return render(request, 'cashier.html')

@login_required
def admin_view(request):
    """Admin dashboard."""
    if request.user.role != 'admin':
        return redirect('home')

    # Get data for admin dashboard
    employees = Employee.objects.all()[:10]  # Limit to 10 for dashboard
    products = Product.objects.filter(is_active=True)[:10]  # Limit to 10 for dashboard
    sales = Sale.objects.all().order_by('-date')[:10]  # Limit to 10 for dashboard

    # Calculate total revenue
    total_revenue = Sale.objects.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(total=Sum('total'))['total'] or 0

    context = {
        'employees': employees,
        'products': products,
        'sales': sales,
        'total_revenue': total_revenue,
    }

    return render(request, 'admin.html', context)

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Cart Views
@login_required
def add_to_cart(request, product_id):
    """Add product to cart."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'sku': product.sku
        }

    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cashier')

@login_required
def remove_from_cart(request, product_id):
    """Remove product from cart."""
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        product_name = cart[str(product_id)]['name']
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, f"{product_name} removed from cart.")
    return redirect('cashier')

@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment created successfully!")
            return redirect('dashboard')  # or some success URL
    else:
        form = PaymentForm()
    return render(request, 'payment_form.html', {'form': form})

@login_required
def create_offline_transaction(request):
    if request.method == 'POST':
        form = OfflineTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Offline transaction created successfully!")
            return redirect('dashboard')  # or some success URL
    else:
        form = OfflineTransactionForm()
    return render(request, 'offline_transaction_form.html', {'form': form})
