from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    Employee, Product, Category, Supplier, Sale, SaleItem,
    Coupon, Customer, Rental, RentalItem, RentalPayment,
    Payment, OfflineTransaction
)
from django.utils import timezone


class EmployeeRegistrationForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = ['username', 'first_name', 'last_name', 'email', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not forms.EmailField().clean(email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role')
        valid_roles = ['ADMIN', 'MANAGER', 'CASHIER', 'EMPLOYEE']
        if role not in valid_roles:
            raise ValidationError(f"Role must be one of {valid_roles}.")
        return role


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'price', 'cost_price', 'quantity',
            'min_stock_level', 'max_stock_level', 'category', 'supplier',
            'product_type', 'rental_daily_rate', 'rental_late_fee_rate', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price is not None and cost_price < 0:
            raise ValidationError("Cost price cannot be negative.")
        return cost_price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        return quantity

    def clean_min_stock_level(self):
        min_stock = self.cleaned_data.get('min_stock_level')
        if min_stock is not None and min_stock < 0:
            raise ValidationError("Minimum stock level cannot be negative.")
        return min_stock

    def clean_max_stock_level(self):
        max_stock = self.cleaned_data.get('max_stock_level')
        if max_stock is not None and max_stock < 0:
            raise ValidationError("Maximum stock level cannot be negative.")
        return max_stock

    def clean_rental_daily_rate(self):
        rate = self.cleaned_data.get('rental_daily_rate')
        if rate is not None and rate < 0:
            raise ValidationError("Rental daily rate cannot be negative.")
        return rate

    def clean_rental_late_fee_rate(self):
        rate = self.cleaned_data.get('rental_late_fee_rate')
        if rate is not None and rate < 0:
            raise ValidationError("Rental late fee rate cannot be negative.")
        return rate


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not forms.EmailField().clean(email):
            raise ValidationError("Enter a valid email address.")
        return email


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['state', 'coupon', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'is_active', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount is not None and (discount < 0 or discount > 100):
            raise ValidationError("Discount percentage must be between 0 and 100.")
        return discount

    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future.")
        return expires_at


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'date_of_birth', 'notes', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not forms.EmailField().clean(email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['customer', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date <= timezone.now():
            raise ValidationError("Due date must be in the future.")
        return due_date


class RentalItemForm(forms.ModelForm):
    class Meta:
        model = RentalItem
        fields = ['product', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity


class RentalPaymentForm(forms.ModelForm):
    class Meta:
        model = RentalPayment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount


class RentalReturnForm(forms.Form):
    return_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        help_text="Leave blank to use current date/time"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        if return_date and return_date > timezone.now():
            raise ValidationError("Return date cannot be in the future.")
        return return_date


# --- ADD THE NEW FORMS BELOW ---


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'  # or specify fields explicitly


class OfflineTransactionForm(forms.ModelForm):
    class Meta:
        model = OfflineTransaction
        fields = '__all__'  # or specify fields explicitly
