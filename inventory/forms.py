from django import forms
from pos_app.models import Product, Category, Supplier


class ProductForm(forms.ModelForm):
    """Form for creating/updating Product — includes validation similar to legacy product validation."""

    class Meta:
        model = Product
        fields = [
            'name',
            'sku',
            'description',
            'price',
            'quantity',
            'min_stock_level',
            'category',
            'supplier',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

    def clean_min_stock_level(self):
        min_stock = self.cleaned_data.get('min_stock_level')
        if min_stock is None or min_stock < 0:
            raise forms.ValidationError("Minimum stock level cannot be negative.")
        return min_stock

    def clean_sku(self):
        sku = self.cleaned_data.get('sku', '').strip()
        if not sku:
            raise forms.ValidationError("SKU cannot be empty.")
        # Check for duplicate SKU (excluding current instance if editing)
        qs = Product.objects.filter(sku__iexact=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A product with this SKU already exists.")
        return sku


class CategoryForm(forms.ModelForm):
    """Form for creating/updating Product Category."""

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Category name cannot be empty.")
        return name


class SupplierForm(forms.ModelForm):
    """Form for creating/updating Supplier details."""

    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Supplier name cannot be empty.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        # Optionally: add more robust email validation or normalization
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        return phone
