from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, Q
from pos_app.models import Product, Category, Supplier, StockMovement
from pos_app.forms import ProductForm


# ---------------------------------------------------------
# PRODUCT LIST VIEW
# ---------------------------------------------------------
class ProductListView(LoginRequiredMixin, ListView):
    """Displays and filters all products in the inventory."""
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related('category', 'supplier')
        )

        # ------------------------ Search ------------------------
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        # ------------------------ Filter by category ------------------------
        category = self.request.GET.get('category')
        if category and category.isdigit():
            queryset = queryset.filter(category_id=category)

        # ------------------------ Low stock ------------------------
        if self.request.GET.get('low_stock') == 'true':
            queryset = queryset.filter(quantity__lte=F('min_stock_level'))

        # ------------------------ Out of stock ------------------------
        if self.request.GET.get('out_of_stock') == 'true':
            queryset = queryset.filter(quantity=0)

        # ------------------------ Active only ------------------------
        active_only = self.request.GET.get('active_only', 'true').lower()
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)

        # ------------------------ Sorting ------------------------
        allowed_sort_fields = {'name', 'price', 'quantity', 'sku', 'created_at'}
        sort = self.request.GET.get('sort', 'name')

        if sort not in allowed_sort_fields:
            sort = 'name'

        order = self.request.GET.get('order', 'asc')
        if order == 'desc':
            sort = f'-{sort}'

        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        context['total_value'] = Product.objects.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

        context['low_stock_count'] = Product.objects.filter(
            quantity__lte=F('min_stock_level'),
            is_active=True
        ).count()

        return context


# ---------------------------------------------------------
# PRODUCT CREATE VIEW
# ---------------------------------------------------------
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f'Product "{form.instance.name}" created successfully!'
        )
        return super().form_valid(form)


# ---------------------------------------------------------
# PRODUCT UPDATE VIEW
# ---------------------------------------------------------
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'

    def get_success_url(self):
        messages.success(self.request, "Product updated successfully!")
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


# ---------------------------------------------------------
# PRODUCT DETAIL VIEW
# ---------------------------------------------------------
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['stock_movements'] = (
            StockMovement.objects.filter(product=self.object)
            .order_by('-created_at')[:20]
        )

        return context


# ---------------------------------------------------------
# UPDATE STOCK VIEW
# ---------------------------------------------------------
@login_required
def update_stock_view(request, pk):
    """Allows staff to adjust stock (increase/decrease) for a product."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            quantity_change = int(request.POST.get('quantity_change', 0))
        except ValueError:
            messages.error(request, "Invalid quantity value.")
            return redirect('product_detail', pk=pk)

        movement_type = request.POST.get('movement_type', 'ADJUSTMENT')
        notes = request.POST.get('notes', '')

        try:
            product.update_stock(
                quantity_change,
                movement_type,
                getattr(request.user, 'employee', None),
                notes
            )
            messages.success(
                request,
                f"Stock updated successfully! New quantity: {product.quantity}"
            )
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('product_detail', pk=product.pk)

    return render(request, 'update_stock.html', {'product': product})
