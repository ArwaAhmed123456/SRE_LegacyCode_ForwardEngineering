from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q, ExpressionWrapper, DecimalField, F

from pos_app.models import Rental, RentalItem, RentalPayment, Product
from pos_app.forms import RentalForm, RentalItemForm, RentalPaymentForm, RentalReturnForm


class RentalListView(LoginRequiredMixin, ListView):
    """Rental list view with search, filters, and pagination."""
    model = Rental
    template_name = 'rentals/rental_list.html'
    context_object_name = 'rentals'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee')

        # Search across customer name, phone, and rental number
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search) |
                Q(rental_number__icontains=search)
            )

        # Filter by rental status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(rental_status=status)

        # Filter overdue rentals if requested
        overdue = self.request.GET.get('overdue', '')
        if overdue.lower() == 'true':
            queryset = queryset.filter(
                rental_status='ACTIVE',
                due_date__lt=timezone.now()
            )

        # Filter by date range
        start_date = self.request.GET.get('start_date', '')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        end_date = self.request.GET.get('end_date', '')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rentals'] = Rental.objects.count()
        context['active_rentals'] = Rental.objects.filter(rental_status='ACTIVE').count()
        context['overdue_rentals'] = Rental.objects.filter(
            rental_status='ACTIVE',
            due_date__lt=timezone.now()
        ).count()
        context['total_revenue'] = Rental.objects.annotate(
            total=Sum(ExpressionWrapper(
                F('items__product__rental_daily_rate') * F('items__quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        ).aggregate(total=Sum('total'))['total'] or 0
        return context


class RentalCreateView(LoginRequiredMixin, CreateView):
    """View to create a new rental."""
    model = Rental
    form_class = RentalForm
    template_name = 'rentals/rental_form.html'
    success_url = reverse_lazy('rentals:rental_list')

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        form.instance.created_by = self.request.user.employee
        messages.success(self.request, f'Rental "{form.instance.rental_number}" created successfully!')
        return super().form_valid(form)


class RentalDetailView(LoginRequiredMixin, DetailView):
    """Detailed view for a single rental."""
    model = Rental
    template_name = 'rentals/rental_detail.html'
    context_object_name = 'rental'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rental_items'] = self.object.rental_items.all()
        context['payments'] = self.object.payments.all()
        return context


@login_required
def add_rental_item_view(request, pk):
    """Add an item to an existing rental."""
    rental = get_object_or_404(Rental, pk=pk)

    if request.method == 'POST':
        form = RentalItemForm(request.POST)
        if form.is_valid():
            try:
                rental.add_item(
                    form.cleaned_data['product'],
                    form.cleaned_data['quantity']
                )
                messages.success(request, "Item added to rental successfully!")
                return redirect('rentals:rental_detail', pk=rental.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RentalItemForm()

    return render(request, 'rentals/add_item.html', {
        'form': form,
        'rental': rental
    })


@login_required
def process_rental_payment_view(request, pk):
    """Process a payment for a rental."""
    rental = get_object_or_404(Rental, pk=pk)

    if request.method == 'POST':
        form = RentalPaymentForm(request.POST)
        if form.is_valid():
            try:
                balance_due = rental.process_payment(
                    form.cleaned_data['amount'],
                    form.cleaned_data['payment_method'],
                    form.cleaned_data['transaction_id'],
                    form.cleaned_data['notes']
                )
                messages.success(request, f"Payment processed successfully! Balance due: ${balance_due}")
                return redirect('rentals:rental_detail', pk=rental.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RentalPaymentForm()

    return render(request, 'rentals/process_payment.html', {
        'form': form,
        'rental': rental
    })


@login_required
def return_rental_item_view(request, pk):
    """Process return of a rental item."""
    rental = get_object_or_404(Rental, pk=pk)

    if request.method == 'POST':
        form = RentalReturnForm(request.POST)
        if form.is_valid():
            try:
                rental.return_item(
                    rental.rental_items.first().product,  # Simplification: returning first item
                    return_date=form.cleaned_data['return_date']
                )
                messages.success(request, "Item returned successfully!")
                return redirect('rentals:rental_detail', pk=rental.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RentalReturnForm()

    return render(request, 'rentals/return_item.html', {
        'form': form,
        'rental': rental
    })


@login_required
def cancel_rental_view(request, pk):
    """Cancel an active rental."""
    rental = get_object_or_404(Rental, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        try:
            rental.cancel_rental(reason)
            messages.success(request, "Rental cancelled successfully!")
            return redirect('rentals:rental_list')
        except ValidationError as e:
            messages.error(request, str(e))

    return render(request, 'rentals/cancel_rental.html', {
        'rental': rental
    })
