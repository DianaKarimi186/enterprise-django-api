from django.urls import path
from .views import (
    ProductListCreateView, 
    ProductDetailView, 
    DashboardView, 
    HTMXCreateProductView, 
    DeleteProductView
)

urlpatterns = [
    # Visual Frontend UI Gates
    path('dashboard/', DashboardView.as_view(), name='product-dashboard'),
    path('dashboard/create/', HTMXCreateProductView.as_view(), name='htmx-create-product'),
    path('dashboard/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    
    # Pure JSON REST API Core Ports
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
