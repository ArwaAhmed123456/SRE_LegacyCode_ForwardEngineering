from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Product list (main inventory dashboard)
    path('', views.ProductListView.as_view(), name='product_list'),

    # Create new product
    path('create/', views.ProductCreateView.as_view(), name='product_create'),

    # Product detail
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Update product details
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),

    # Update stock (Increase/Decrease)
    path('<int:pk>/stock/update/', views.update_stock_view, name='update_stock'),
]
