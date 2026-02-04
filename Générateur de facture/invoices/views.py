from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from decimal import Decimal
from .models import Product, Invoice, InvoiceItem, Client
from .forms import ProductForm, InvoiceForm, InvoiceItemFormSet, ClientForm
from django.db.models import Sum, Count, F
from django.utils import timezone


# ============ VUES DASHBOARD ============

class DashboardView(ListView):
    template_name = 'invoices/dashboard_v2.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        return Invoice.objects.all().order_by('-date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stats globales
        context['total_invoices'] = Invoice.objects.count()
        context['total_clients'] = Client.objects.count()
        
        # Chiffre d'affaires total
        total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['total_revenue'] = total_revenue
        
        # Valeur du stock (Prix unitaire * Quantité en stock)
        # Note: ceci est une estimation car stock_quantity peut changer
        stock_value = Product.objects.aggregate(
            total_value=Sum(F('unit_price') * F('stock_quantity'))
        )['total_value'] or 0
        context['stock_value'] = stock_value
        
        # Produits en stock faible (< 5)
        context['low_stock_products'] = Product.objects.filter(stock_quantity__lt=5)
        
        return context


# ============ VUES CLIENTS ============

class ClientListView(ListView):
    model = Client
    template_name = 'invoices/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(company__icontains=search)
        return queryset


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'invoices/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Client créé avec succès!')
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'invoices/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, 'Client modifié avec succès!')
        return super().form_valid(form)


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'invoices/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Client supprimé avec succès!')
        return super().delete(request, *args, **kwargs)

# PDF imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO


# ============ VUES PRODUITS ============

class ProductListView(ListView):
    """Liste des produits avec pagination"""
    model = Product
    template_name = 'invoices/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class ProductCreateView(CreateView):
    """Création d'un produit"""
    model = Product
    form_class = ProductForm
    template_name = 'invoices/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Produit créé avec succès!')
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    """Modification d'un produit"""
    model = Product
    form_class = ProductForm
    template_name = 'invoices/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Produit modifié avec succès!')
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    """Suppression d'un produit"""
    model = Product
    template_name = 'invoices/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Produit supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


# ============ VUES FACTURES ============

class InvoiceListView(ListView):
    """Liste des factures avec pagination"""
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10


    context_object_name = 'invoices'
    paginate_by = 10


class InvoiceDeleteView(DeleteView):
    """Suppression d'une facture"""
    model = Invoice
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoice_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Facture supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


def invoice_create(request):
    """Création d'une facture avec sélection de produits"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Créer la facture
                invoice = form.save()
                
                # Créer les lignes de facture
                has_items = False
                for item_form in formset:
                    if item_form.is_valid():
                        product = item_form.cleaned_data.get('product')
                        quantity = item_form.cleaned_data.get('quantity')
                        
                        if product and quantity:
                            InvoiceItem.objects.create(
                                invoice=invoice,
                                product=product,
                                quantity=quantity,
                                unit_price=product.unit_price
                            )
                            
                            # Déduire du stock si demandé
                            if form.cleaned_data.get('deduct_stock'):
                                product.stock_quantity -= quantity
                                product.save()

                            has_items = True
                
                if not has_items:
                    messages.error(request, 'Veuillez ajouter au moins un produit à la facture.')
                    invoice.delete()
                    return render(request, 'invoices/invoice_form.html', {
                        'form': form,
                        'formset': formset,
                    })
                
                # Calculer le total
                invoice.calculate_total()
                
                messages.success(request, f'Facture {invoice.invoice_number} créée avec succès!')
                return redirect('invoice_detail', pk=invoice.pk)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
    })


def invoice_duplicate(request, pk):
    """Dupliquer une facture existante"""
    original_invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        # Réutiliser la logique de création
        return invoice_create(request)
    else:
        # Pré-remplir le formulaire avec les données de la facture d'origine
        form = InvoiceForm(initial={
            'client': original_invoice.client,
            'include_vat': original_invoice.include_vat,
            'date': timezone.now().date(),
        })
        
        # Pré-remplir les items
        initial_items = []
        for item in original_invoice.items.all():
            initial_items.append({
                'product': item.product,
                'quantity': item.quantity,
            })
        
        formset = InvoiceItemFormSet(initial=initial_items)
            
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': f"Dupliquer la facture {original_invoice.invoice_number}"
    })


def invoice_detail(request, pk):
    """Détail d'une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
    })


def invoice_pdf(request, pk):
    """Génération PDF de la facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Créer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Couleurs
    PRIMARY_COLOR = colors.HexColor('#3b40cc')  # Bleu violet comme sur l'image
    TEXT_COLOR = colors.HexColor('#2c3e50')
    LIGHT_GRAY = colors.HexColor('#f3f4f6')
    
    # Styles personnalisés
    # 1. En-tête (Sender Info)
    sender_name_style = ParagraphStyle(
        'SenderName',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=2,
    )
    
    sender_info_style = ParagraphStyle(
        'SenderInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        leading=12,
    )
    
    # 2. Titre Facture
    invoice_title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceBefore=20,
        spaceAfter=5,
    )
    
    date_sent_style = ParagraphStyle(
        'DateSent',
        parent=styles['Normal'],
        fontSize=10,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
    )
    
    # --- HEADER SECTION ---
    # Colonne Gauche: Émetteur
    sender_details = [
        Paragraph("AllToo", sender_name_style),
        Paragraph("161 Av. de Verdun<br/>94200 Ivry-sur-Seine<br/>01 84 60 60 29<br/>contact@alltoo.fr", sender_info_style),
    ]
    
    # Colonne Droite: Siret/TVA (supprimé à la demande)
    # sender_legal laissé vide
    sender_legal = []
    
    header_table = Table([[sender_details, sender_legal]], colWidths=[10*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    
    elements.append(Spacer(1, 1*cm))
    
    # --- TITLE SECTION ---
    elements.append(Paragraph(f"Facture {invoice.invoice_number.split('-')[-1] if '-' in invoice.invoice_number else invoice.invoice_number}", invoice_title_style))
    elements.append(Paragraph(f"Envoyée le {invoice.date.strftime('%d/%m/%Y')}", date_sent_style))
    
    elements.append(Spacer(1, 1*cm))
    
    # --- CLIENT & DETAILS SECTION ---
    # Boite grise pour le client
    client_box_style = ParagraphStyle(
        'ClientBox',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
    )
    
    client_title_style = ParagraphStyle(
        'ClientTitle',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        spaceAfter=5,
    )

    client = invoice.client
    client_address = f"{client.address}<br/>{client.city} {getattr(client, 'country', '')}" if client else ""
    client_siret = f"<br/><br/>Siret : {getattr(client, 'siret', '')}" if client and getattr(client, 'siret', '') else ""
    
    client_text = [
        Paragraph("Facture pour", client_title_style),
        Paragraph(f"{client.name if client else ''}<br/>{client.company if client and client.company else ''}<br/>{client_address}{client_siret}", client_box_style)
    ]
    
    # Détails à droite
    details_label_style = ParagraphStyle('DetailsLabel', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
    details_value_style = ParagraphStyle('DetailsValue', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)
    
    # Date échéance = Date + 30 jours par défaut
    due_date = invoice.date + timezone.timedelta(days=30)
    
    details_data = [
        [Paragraph("N° de facture", details_label_style), Paragraph(f"{invoice.invoice_number.split('-')[-1]}", details_value_style)],
        [Paragraph("Projet", details_label_style), Paragraph("-", details_value_style)],
        [Paragraph("Date d'échéance", details_label_style), Paragraph(f"{due_date.strftime('%d/%m/%Y')}", details_value_style)],
    ]
    
    details_table = Table(details_data, colWidths=[4*cm, 3*cm])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    # Layout Client / Details : Table principale de cette section
    # La colonne de gauche (Client) a un fond gris
    wrapper_data = [[client_text, details_table]]
    wrapper_table = Table(wrapper_data, colWidths=[10*cm, 8*cm])
    wrapper_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), LIGHT_GRAY), # Fond gris pour client
        ('LEFTPADDING', (0,0), (0,0), 6),
        ('RIGHTPADDING', (0,0), (0,0), 6),
        ('TOPPADDING', (0,0), (0,0), 6),
        ('BOTTOMPADDING', (0,0), (0,0), 6),
        ('LEFTPADDING', (1,0), (1,0), 20), # Espace avant détails
    ]))
    
    elements.append(wrapper_table)
    elements.append(Spacer(1, 1.5*cm))
    
    # --- PRODUCTS TABLE ---
    # Header
    
    products_data = [['Description', 'Qté', 'Prix unitaire', 'Prix HT']]
    
    for item in invoice.items.all():
        products_data.append([
            Paragraph(item.product.name, styles['Normal']),
            str(item.quantity),
            f"{item.unit_price} €",
            f"{item.subtotal} €"
        ])
    
    # Table Widths
    # Total width approx 18cm
    t_widths = [9.5*cm, 1.5*cm, 3.5*cm, 3.5*cm]
    
    products_table = Table(products_data, colWidths=t_widths)
    
    table_style = [
        # Header Style
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'), # Description left
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'), # Others right
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 6),
        
        # Rows Style
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 0, colors.white), # Hide header bottom line if needed
    ]
    
    products_table.setStyle(TableStyle(table_style))
    elements.append(products_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # --- TOTALS ---
    subtotal = sum(item.subtotal for item in invoice.items.all())
    
    totals_data = []
    
    # Style pour les labels et valeurs de totaux
    total_label_style = ParagraphStyle('TotalLabel', parent=styles['Normal'], fontSize=10)
    total_val_style = ParagraphStyle('TotalVal', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)
    
    totals_data.append(['', '', 'Sous-total', f"{subtotal} €"])
    
    if invoice.include_vat:
        vat_amount = subtotal * Decimal('0.20')
        totals_data.append(['', '', 'TVA (20%)', f"{vat_amount:.2f} €"])
        final_total = invoice.total_amount
        total_text = "Total TTC"
    else:
        final_total = subtotal
        total_text = "Total"
        
    totals_table = Table(totals_data, colWidths=t_widths)
    totals_table.setStyle(TableStyle([
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, 0), (-1, -1), 'Helvetica'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    
    # Grand Total avec fond gris/bleu
    grand_total_data = [['', '', Paragraph(f"<b>{total_text}</b>", total_label_style), Paragraph(f"<b>{final_total} €</b>", ParagraphStyle('GT', parent=total_val_style, fontSize=12, textColor=PRIMARY_COLOR)) ]]
    grand_total_table = Table(grand_total_data, colWidths=t_widths)
    grand_total_table.setStyle(TableStyle([
        ('BACKGROUND', (-2, 0), (-1, 0), LIGHT_GRAY),
        ('ALIGN', (-2, 0), (-1, 0), 'RIGHT'),
        ('TOPPADDING', (-2, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (-2, 0), (-1, 0), 10),
    ]))
    elements.append(grand_total_table)
    
    elements.append(Spacer(1, 2*cm))
    
    # --- FOOTER ---
    # TVA non applicable...
    footer_text = "TVA non applicable, art. 293B du CGI"
    if invoice.include_vat:
        footer_text = "TVA incluse au taux de 20%"
        
    footer_para = Paragraph(
        f"{footer_text}<br/>En votre aimable règlement à réception de facture par virement à l'ordre de la société AllToo.<br/>Aucun escompte prévu pour règlement anticipé.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
    )
    elements.append(footer_para)
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le PDF
    pdf = buffer.getvalue()
    buffer.close()
    
    # Créer la réponse HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_{invoice.invoice_number}.pdf"'
    response.write(pdf)
    
    return response


def home(request):
    """Page d'accueil"""
    return render(request, 'invoices/home.html', {
        'total_products': Product.objects.count(),
        'total_invoices': Invoice.objects.count(),
    })
