from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from . import views

app_name = 'pos_app'

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('register/', views.EmployeeRegistrationView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Profile and Dashboard (login required)
    path('profile/', login_required(views.profile_view), name='profile'),
    path('dashboard/', login_required(views.dashboard_view), name='dashboard'),
    path('home/', login_required(views.home_view), name='home'),

    # Role-based views (example: cashier, admin)
    path('cashier/', login_required(views.cashier_view), name='cashier'),
    path('admin/', login_required(views.admin_view), name='admin'),

    # Product Management URLs (permission required)
    path('products/', login_required(views.ProductListView.as_view()), name='product_list'),
    path('products/create/', permission_required('pos_app.add_product')(views.ProductCreateView.as_view()), name='product_create'),
    path('products/<int:pk>/update/', permission_required('pos_app.change_product')(views.ProductUpdateView.as_view()), name='product_update'),
    path('products/<int:pk>/delete/', permission_required('pos_app.delete_product')(views.ProductDeleteView.as_view()), name='product_delete'),

    # Category Management URLs
    path('categories/', login_required(views.CategoryListView.as_view()), name='category_list'),
    path('categories/create/', permission_required('pos_app.add_category')(views.CategoryCreateView.as_view()), name='category_create'),
    path('categories/<int:pk>/update/', permission_required('pos_app.change_category')(views.CategoryUpdateView.as_view()), name='category_update'),
    path('categories/<int:pk>/delete/', permission_required('pos_app.delete_category')(views.CategoryDeleteView.as_view()), name='category_delete'),

    # Supplier Management URLs
    path('suppliers/', login_required(views.SupplierListView.as_view()), name='supplier_list'),
    path('suppliers/create/', permission_required('pos_app.add_supplier')(views.SupplierCreateView.as_view()), name='supplier_create'),
    path('suppliers/<int:pk>/update/', permission_required('pos_app.change_supplier')(views.SupplierUpdateView.as_view()), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', permission_required('pos_app.delete_supplier')(views.SupplierDeleteView.as_view()), name='supplier_delete'),

    # Cart and Checkout URLs
    path('add_to_cart/<int:product_id>/', login_required(views.add_to_cart), name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', login_required(views.remove_from_cart), name='remove_from_cart'),
    path('checkout/', login_required(views.checkout), name='checkout'),

    # Sales Processing URLs
    path('sales/', login_required(views.SaleListView.as_view()), name='sale_list'),
    path('sales/create/', permission_required('pos_app.add_sale')(views.SaleCreateView.as_view()), name='sale_create'),
    path('sales/<int:pk>/', login_required(views.SaleDetailView.as_view()), name='sale_detail'),
    path('sales/<int:pk>/payment/', permission_required('pos_app.change_sale')(views.process_payment_view), name='process_payment'),

    # AJAX URLs for cart operations (secured by login)
    path('api/cart/add/', login_required(views.add_to_cart_view), name='add_to_cart_ajax'),

    # Employee Management URLs (Admin or HR role ideally)
    path('employees/', permission_required('pos_app.view_employee')(views.EmployeeListView.as_view()), name='employee_list'),

    # Reports URL
    path('reports/', permission_required('pos_app.view_reports')(views.reports), name='reports'),

    # Payment and Offline Transaction URLs
    path('payments/create/', login_required(views.create_payment), name='create_payment'),
    path('offline-transactions/create/', login_required(views.create_offline_transaction), name='create_offline_transaction'),
]
