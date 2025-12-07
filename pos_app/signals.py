from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleItem

@receiver(post_save, sender=SaleItem)
def update_inventory_on_sale(sender, instance, created, **kwargs):
    if created:
        quantity = instance.quantity
        if quantity > 0:
            try:
                instance.product.sell(quantity, instance.sale.employee, f"Sale #{instance.sale.id}")
            except Exception as e:
                # Log or handle insufficient stock or other issues
                print(f"Error updating inventory for SaleItem {instance.id}: {e}")
