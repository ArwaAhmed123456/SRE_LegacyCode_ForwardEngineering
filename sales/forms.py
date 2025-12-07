from django import forms
from django.core.exceptions import ValidationError
from pos_app.models import Sale, Payment

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'payment_method', 'discount_percentage', 'shipping_cost', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount is not None and (discount < 0 or discount > 100):
            raise ValidationError('Discount must be between 0 and 100 percent')
        return discount

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError('Amount must be greater than 0')
        return amount

