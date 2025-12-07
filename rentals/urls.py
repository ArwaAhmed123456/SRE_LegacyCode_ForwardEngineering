from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.RentalListView.as_view(), name='rental_list'),
    path('create/', views.RentalCreateView.as_view(), name='rental_create'),
    path('<int:pk>/', views.RentalDetailView.as_view(), name='rental_detail'),
    path('<int:pk>/add-item/', views.add_rental_item_view, name='add_rental_item'),
    path('<int:pk>/payment/', views.process_rental_payment_view, name='process_rental_payment'),
    path('<int:pk>/return/', views.return_rental_item_view, name='return_rental_item'),
    path('<int:pk>/cancel/', views.cancel_rental_view, name='cancel_rental'),
]
