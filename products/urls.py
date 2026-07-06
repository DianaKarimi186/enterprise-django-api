from django.urls import path
from .views import ProductListCreateView, ProductDetailView, DashboardView, DeleteProductView, HTMXCreateProductView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='product-dashboard'),
    path('dashboard/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    # New gateway for HTMX asynchronous product submission
    path('dashboard/create/', HTMXCreateProductView.as_view(), name='htmx-create-product'),
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]