from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class Product(models.Model):
    """Modèle pour les produits"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire"
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Quantité en stock"
    )
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de péremption"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.unit_price}€"


class Client(models.Model):
    """Modèle pour les clients"""
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    company = models.CharField(max_length=200, blank=True, verbose_name="Entreprise")
    siret = models.CharField(max_length=14, blank=True, verbose_name="SIRET")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']

    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name


class Invoice(models.Model):
    """Modèle pour les factures"""
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Client",
        related_name="invoices"
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de facture"
    )
    date = models.DateField(default=timezone.now, verbose_name="Date")
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant total"
    )
    include_vat = models.BooleanField(
        default=False,
        verbose_name="Inclure la TVA (20%)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.total_amount}€"

    def calculate_total(self):
        """Calcule le montant total de la facture"""
        total = sum(item.subtotal for item in self.items.all())
        if self.include_vat:
            total = total * Decimal('1.20')
        self.total_amount = total
        self.save()
        return total

    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de facture si nécessaire"""
        if not self.invoice_number:
            # Format: FAC-YYYYMMDD-XXX
            today = timezone.now()
            date_str = today.strftime('%Y%m%d')
            # Compte les factures du jour
            count = Invoice.objects.filter(
                invoice_number__startswith=f'FAC-{date_str}'
            ).count()
            self.invoice_number = f'FAC-{date_str}-{count + 1:03d}'
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Modèle pour les lignes de facture (produits dans une facture)"""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Facture"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Produit"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantité"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix unitaire"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sous-total"
    )

    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
        unique_together = ['invoice', 'product']

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.subtotal}€"

    def save(self, *args, **kwargs):
        """Calcule automatiquement le sous-total"""
        # Utilise le prix actuel du produit si non spécifié
        if not self.unit_price:
            self.unit_price = self.product.unit_price
        # Calcule le sous-total
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Met à jour le total de la facture
        self.invoice.calculate_total()
