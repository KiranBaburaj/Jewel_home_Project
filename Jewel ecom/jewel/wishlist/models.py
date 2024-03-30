# models.py
from django.db import models
from user.models import User
from product.models import Products  # Import your product model

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Products)

    def __str__(self):
        return f"Wishlist for {self.user.username}"
