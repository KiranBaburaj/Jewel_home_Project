from decimal import Decimal
from django.db import models
from user.models import User



class Coupon(models.Model):
    # Existing fields
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage')])
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_purchase_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    maximum_discount_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    # Additional fields for first purchase coupon


    def __str__(self):
        return self.code
    
    @staticmethod
    def calculate_discounted_total(discount_type, total_cart_value, discount_amount, discount_percentage):
        total_cart_value = Decimal(str(total_cart_value))  # Convert total_cart_value to Decimal

        if discount_type == 'fixed':
            discounted_total = max(Decimal('0.00'), total_cart_value - Decimal(str(discount_amount)))
        elif discount_type == 'percentage':
            discount_amount = total_cart_value * (Decimal(str(discount_percentage)) / Decimal('100.00'))
            discounted_total = max(Decimal('0.00'), total_cart_value - discount_amount)
        else:
            discounted_total = total_cart_value

        return float(discounted_total)  # Convert Decimal to float before returning



class ReferralCoupon(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=20, unique=True)
    referrals_made = models.PositiveIntegerField(default=0)  # Track the number of referrals made by the user
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

from product.models import Products,Category
from django.core.validators import MaxValueValidator

class ProductOffers(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE, related_name='offer')
    name = models.CharField(max_length=100, default="Default Offer Name")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MaxValueValidator(50)])
    start_date = models.DateField()
    end_date = models.DateField()

class CategoryOffers(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='offer')
    name = models.CharField(max_length=100, default="Default Offer Name")  # Provide a default value
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2 ,validators=[MaxValueValidator(50)])
    start_date = models.DateField()
    end_date = models.DateField()
