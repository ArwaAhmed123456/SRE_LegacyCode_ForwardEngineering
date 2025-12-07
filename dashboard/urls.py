from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Home
    path('', views.dashboard_view, name='dashboard'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Employee Registration (Class-based View)
    path('register/', views.EmployeeRegistrationView.as_view(), name='register'),
]
