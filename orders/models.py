from datetime import timezone

from django.db import models

# Create your models here.
from django.db import models
from products.models import ProductSize
from django.contrib.auth.models import User


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="invoices")
    address = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.FloatField()
    hide = models.BooleanField(default=False)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product_size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()

