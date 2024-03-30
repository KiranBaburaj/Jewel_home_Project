# models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from product.models import Products, Size
from user.models import Order,User



class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.timestamp}"

from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def add_funds(self, amount):
        self.balance += amount
        self.save()
        Transaction.objects.create(user=self.user, transaction_type='credit', amount=amount)


    def deduct_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            Transaction.objects.create(user=self.user, transaction_type='debit', amount=amount)
        else:
            raise ValueError("Insufficient funds")

    def check_balance(self):
        return self.balance

    def __str__(self):
        return f"Wallet of {self.user.username}"
    
    def refund_to_wallet(self):
        # Check if the payment status is 'Completed' and the order status is 'Cancelled'
        if self.payment_status == 'Completed' and self.status == 'Cancelled':
            # Refund the total order value to the user's wallet
            user_wallet = self.user.wallet
            user_wallet.add_funds(self.total_value)
            # Update the payment status to 'Refunded' and save the order
            self.payment_status = 'Refunded'
            self.save()



from django.db import models
from django.conf import settings
from product.models import Products





class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} by {self.user.username} at {self.timestamp}"



class Rating(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Stars"

from django.db import models
from django.utils import timezone



class Reason(models.Model):
    REASON_CHOICES = (

        ('Customer changed mind', 'Customer changed mind'),
        ('Delivery delay', 'Delivery delay'),    
        ('Wrong size/color ordered', 'Wrong size/color ordered'),
        ('Duplicate order', 'Duplicate order'),
        ('Other', 'Other'),
           )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
