from django.db import models

# Create your models here.
from django.db import db

class Product(db.Model):
    name = db.CharField(max_length=255)
    description = db.TextField(blank=True, null=True)
    price = db.DecimalField(max_digits=10, decimal_places=2)
    stock = db.IntegerField(default=0)
    created_at = db.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name