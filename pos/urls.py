from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Dashboard (Home)
    path('', include('dashboard.urls')),

    # Inventory / Products
    path('products/', include('inventory.urls')),

    # Sales
    path('sales/', include('sales.urls')),

    # Rentals
    path('rentals/', include('rentals.urls')),

    # Authentication + Employee App
    path('pos/', include('pos_app.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
