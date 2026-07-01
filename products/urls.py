from django.urls import path
from .views import ProductListCreateView, ProductDetailView, DashboardView


urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='product-dashboard'),
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]