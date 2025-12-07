from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, DecimalField
from django.utils import timezone

from pos_app.models import Product, Sale, SaleItem, Employee
from pos_app.forms import EmployeeRegistrationForm


@login_required
def dashboard_view(request):
    """
    Main dashboard for the POS system.
    Equivalent to the legacy 'POSApplication' main screen.
    """

    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)

    # --------------------------
    # SALES STATISTICS
    # --------------------------
    today_sales = Sale.objects.filter(
        created_at__date=today,
        state='COMPLETED'
    )

    today_total = today_sales.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(
        total=Sum('total')
    )['total'] or 0

    today_count = today_sales.count()

    # Monthly Sales (from 1st of month → today)
    month_sales = Sale.objects.filter(
        created_at__date__gte=today.replace(day=1),
        state='COMPLETED'
    )

    month_total = month_sales.annotate(
        total=Sum(ExpressionWrapper(
            F('items__product__price') * F('items__quantity'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ))
    ).aggregate(
        total=Sum('total')
    )['total'] or 0

    # --------------------------
    # INVENTORY STATISTICS
    # --------------------------
    total_products = Product.objects.count()

    low_stock_count = Product.objects.filter(
        quantity__lte=F('min_stock_level')
    ).count()

    out_of_stock_count = Product.objects.filter(quantity=0).count()

    # --------------------------
    # EMPLOYEE (TEMP CUSTOMER COUNT)
    # --------------------------
    total_employees = Employee.objects.count()

    # --------------------------
    # RECENT SALES LIST
    # --------------------------
    recent_sales = Sale.objects.filter(
        state='COMPLETED'
    ).order_by('-created_at')[:10]

    # --------------------------
    # LOW STOCK PRODUCTS LIST
    # --------------------------
    low_stock_products = Product.objects.filter(
        quantity__lte=F('min_stock_level')
    ).order_by('quantity')[:5]

    # --------------------------
    # TOP SELLING PRODUCTS (30 DAYS)
    # FIXED revenue formula
    # --------------------------
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=thirty_days_ago,
        sale__state='COMPLETED'
    ).annotate(
        product_name=F('product__name')
    ).values('product_name').annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(ExpressionWrapper(
            F('product__price') * F('quantity'),
            output_field=FloatField()
        ))
    ).order_by('-quantity_sold')[:5]

    # --------------------------
    # DAILY SALES FOR CHART (7 DAYS)
    # --------------------------
    daily_sales_data = []
    for i in range(6, -1, -1):
        date = today - timezone.timedelta(days=i)
        daily_sales = Sale.objects.filter(
            created_at__date=date,
            state='COMPLETED'
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
            'count': daily_sales['count'] or 0,
        })

    context = {
        'today_total': today_total,
        'today_count': today_count,
        'month_total': month_total,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,

        # temporarily employees = customers  
        'total_customers': total_employees,

        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        'daily_sales_data': daily_sales_data,
    }

    return render(request, 'dashboard.html', context)


# =====================================================================
# LOGIN VIEW — Modern, polished
# =====================================================================
def login_view(request):
    """User Login — Equivalent to legacy login screen."""
    
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# =====================================================================
# LOGOUT VIEW
# =====================================================================
def logout_view(request):
    """Logout — Equivalent to legacy logout functionality."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# =====================================================================
# EMPLOYEE REGISTRATION
# =====================================================================
class EmployeeRegistrationView:
    """Registration view for new employees."""

    def get(self, request):
        form = EmployeeRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.get_full_name() or user.username}!')
            return redirect('login')
        return render(request, 'register.html', {'form': form})

    @classmethod
    def as_view(cls):
        def view(request):
            self = cls()
            return self.post(request) if request.method == 'POST' else self.get(request)
        return view
