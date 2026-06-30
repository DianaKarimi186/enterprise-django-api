from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Default Django Admin panel
    path('api/products/', include('products.urls')),
]