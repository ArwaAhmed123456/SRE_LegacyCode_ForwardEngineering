from django.urls import path
from . import views

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('new/', views.SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('<int:pk>/payment/', views.process_payment_view, name='process_payment'),
]
