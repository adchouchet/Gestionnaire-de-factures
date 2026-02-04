from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    
    # URLs Produits
    path('produits/', views.ProductListView.as_view(), name='product_list'),
    path('produits/nouveau/', views.ProductCreateView.as_view(), name='product_create'),
    path('produits/<int:pk>/modifier/', views.ProductUpdateView.as_view(), name='product_update'),
    path('produits/<int:pk>/supprimer/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # URLs Factures
    path('factures/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('factures/nouvelle/', views.invoice_create, name='invoice_create'),
    path('factures/<int:pk>/dupliquer/', views.invoice_duplicate, name='invoice_duplicate'),
    path('factures/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('factures/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('factures/<int:pk>/supprimer/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # URLs Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/nouveau/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/modifier/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/supprimer/', views.ClientDeleteView.as_view(), name='client_delete'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
