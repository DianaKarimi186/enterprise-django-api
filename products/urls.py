from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    DashboardView,
    HTMXCreateProductView,
    HTMXEditProductView,
    HTMXUpdateProductView,
    DeleteProductView,
    ProductProcessView,
    TaskStatusView,
)

urlpatterns = [
    # Visual Frontend UI Gates
    path('dashboard/', DashboardView.as_view(), name='product-dashboard'),
    path('dashboard/create/', HTMXCreateProductView.as_view(), name='htmx-create-product'),
    path('dashboard/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    path('dashboard/edit/<int:pk>/',HTMXEditProductView.as_view(),name='htmx-edit-product'),
    path('dashboard/update/<int:pk>/',HTMXUpdateProductView.as_view(),name='htmx-update-product'),
    
    # Pure JSON REST API Core Ports
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/process/', ProductProcessView.as_view(),name='product-process'),
    path('tasks/<str:task_id>/',TaskStatusView.as_view(),name='task-status',),
]
