from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, F, Q, ExpressionWrapper, DecimalField
from pos_app.models import Sale, SaleItem, Product, Employee
from pos_app.forms import SaleForm, SaleItemForm


class SaleListView(LoginRequiredMixin, ListView):
    """Sale list view - equivalent to legacy sales history."""
    model = Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee')

        # Filters
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(sale_status=status)

        date_from = self.request.GET.get('date_from', '')
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)

        date_to = self.request.GET.get('date_to', '')
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)

        employee = self.request.GET.get('employee', '')
        if employee:
            queryset = queryset.filter(employee__id=employee)

        # Search by invoice number
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(invoice_number__icontains=search)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['total_sales'] = Sale.objects.filter(
            sale_status=Sale.SaleStatus.COMPLETED
        ).count()
        context['total_revenue'] = Sale.objects.filter(
            sale_status=Sale.SaleStatus.COMPLETED
        ).annotate(
            total=Sum(ExpressionWrapper(
                F('items__product__price') * F('items__quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        ).aggregate(total=Sum('total'))['total'] or 0
        return context


class SaleCreateView(LoginRequiredMixin, CreateView):
    """Sale create view - equivalent to legacy sale processing."""
    model = Sale
    form_class = SaleForm
    template_name = 'sale_form.html'
    success_url = reverse_lazy('sale_list')

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        form.instance.sale_status = Sale.SaleStatus.PENDING
        messages.success(self.request, "Sale created successfully!")
        return super().form_valid(form)


class SaleDetailView(LoginRequiredMixin, DetailView):
    """Sale detail view."""
    model = Sale
    template_name = 'sale_detail.html'
    context_object_name = 'sale'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale_items'] = SaleItem.objects.filter(sale=self.object).select_related('product')
        return context


@login_required
def add_to_cart_view(request):
    """Add product to cart - legacy cart functionality."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, pk=product_id)

        # Get or create pending sale for this user
        sale, created = Sale.objects.get_or_create(
            employee=request.user.employee,
            sale_status=Sale.SaleStatus.PENDING,
            defaults={}
        )

        # Check if product already in cart
        sale_item, item_created = SaleItem.objects.get_or_create(
            sale=sale,
            product=product,
            defaults={'quantity': 0, 'unit_price': product.price}
        )

        if not item_created:
            sale_item.quantity += quantity
        else:
            sale_item.quantity = quantity

        sale_item.save()

        # Update sale total
        sale.update_total()
        sale.save()

        messages.success(request, f"Added {quantity} x {product.name} to cart")
        return redirect('sale_create')

    return redirect('sale_create')


@login_required
def process_payment_view(request, pk):
    """Process payment - equivalent to legacy payment processing."""
    sale = get_object_or_404(Sale, pk=pk, employee=request.user.employee)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount_paid = float(request.POST.get('amount_paid', 0))

        try:
            with transaction.atomic():
                # Update sale with payment info
                sale.payment_method = payment_method
                sale.amount_paid = amount_paid
                sale.sale_status = Sale.SaleStatus.COMPLETED
                sale.completed_at = timezone.now()
                sale.save()

                # Update inventory
                for item in sale.sale_items.all():
                    item.product.update_stock(
                        -item.quantity,
                        'SALE',
                        request.user.employee,
                        f"Sale #{sale.invoice_number}"
                    )

                messages.success(request, f"Payment processed successfully! Invoice: {sale.invoice_number}")
                return redirect('sale_detail', pk=sale.pk)

        except ValidationError as e:
            messages.error(request, f"Payment failed: {str(e)}")

    return render(request, 'process_payment.html', {'sale': sale})
