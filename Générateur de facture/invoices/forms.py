from django import forms
from django.forms import formset_factory
from .models import Product, Invoice, InvoiceItem, Client


class ProductForm(forms.ModelForm):
    """Formulaire pour les produits"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price', 'stock_quantity', 'expiration_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Description du produit',
                'rows': 4
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0',
                'min': '0'
            }),
            'expiration_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-input',
                'type': 'date'
            }),        }


class ClientForm(forms.ModelForm):
    """Formulaire pour les clients"""
    class Meta:
        model = Client
        fields = ['name', 'company', 'siret', 'phone', 'email', 'address', 'city', 'country']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nom complet'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Entreprise (optionnel)'
            }),
            'siret': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'SIRET (optionnel)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Téléphone (optionnel)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email (optionnel)'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Adresse (optionnel)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ville (optionnel)'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Pays (optionnel)'
            }),
        }


class InvoiceForm(forms.ModelForm):
    """Formulaire pour les factures"""
    deduct_stock = forms.BooleanField(
        required=False,
        initial=False,
        label="Retirer du stock",
        help_text="Si coché, la quantité des produits sera déduite du stock"
    )

    class Meta:
        model = Invoice
        fields = ['client', 'date', 'include_vat']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-input'
            }),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }


class InvoiceItemForm(forms.Form):
    """Formulaire pour les lignes de facture"""
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input product-select'
        })
    )
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-input quantity-input',
            'placeholder': '1',
            'min': '1'
        })
    )


# Formset pour ajouter plusieurs produits à une facture
InvoiceItemFormSet = formset_factory(
    InvoiceItemForm,
    extra=1,
    can_delete=False
)

