# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from product.models import Products, Size

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='custom_user_set',  # Add a related_name
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Add a related_name
    )
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"
    

    from django.db import models
from user.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()


        return super().save(*args, **kwargs)
    
    def total_cart_value(self):
        # Calculate the total value of items in the cart
        total_value = round(sum(item.total_price() for item in self.items.all()),0)
        return total_value
    

from django.db import models
from django.utils import timezone
from product.models import Products, Size
from user.models import User

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)  # Set auto_now to True
    offer_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # New field for offer price


    def clean(self):
        # Check if the selected quantity exceeds the available stock
        if self.quantity > self.size.stock:
            raise ValidationError(f"Only {self.size.stock} units available in stock for {self.size.measurement}")


    def __str__(self):
        return f"{self.quantity} x {self.size.measurement} of {self.product.name} in {self.cart}"


    class Meta:
        unique_together = ('cart', 'product', 'size')  # Ensure unique items in the cart


    def total_price(self):
        return round(self.offer_price * self.quantity,0)


    def save(self, *args, **kwargs):
        # Check if the selected quantity exceeds the maximum allowed per person
        max_quantity_per_person = 3  # You can adjust this value
        user_cart_items = CartItem.objects.filter(cart=self.cart, product=self.product).exclude(pk=self.pk)
        total_quantity = sum(item.quantity for item in user_cart_items) + self.quantity


        if total_quantity > max_quantity_per_person:
            raise ValidationError(f"You can add only up to {max_quantity_per_person} units of item to your cart.")
            

        super().save(*args, **kwargs)


# models.py




from django.db import models
from user.models import User
from product.models import Size, Products


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    original_street_address = models.CharField(max_length=255, blank=True, null=True)
    original_city = models.CharField(max_length=100, blank=True, null=True)
    original_state = models.CharField(max_length=100, blank=True, null=True)
    original_postal_code = models.CharField(max_length=20, blank=True, null=True)
    original_country = models.CharField(max_length=100, blank=True, null=True)
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    coupon_discount  = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # New field for delivery charge

    COD = 'COD'
    RAZORPAY = 'Razorpay'
    WALLET = 'Wallet'
    WALLET_AND_RAZORPAY = 'WalletandRazorpay'

    PAYMENT_METHOD_CHOICES = [
    (COD, 'COD'),
    (RAZORPAY, 'Razorpay'),
    (WALLET, 'Wallet'),
    (WALLET_AND_RAZORPAY, 'Wallet and Razorpay'),  # Corrected value
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=COD)

# Payment status choices
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    REFUNDED = 'Refunded'

    PAYMENT_STATUS_CHOICES = [
    (PENDING, 'Pending'),
    (REFUNDED, 'Refunded'),
    (COMPLETED, 'Completed'),
    ]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)

    
    # Status choices
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    RETURNED = 'Returned'


    STATUS_CHOICES = [
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
        (RETURNED, 'Returned'),

    ]


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PROCESSING)
    wallet = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cod = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    razor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)  # Add this line
    original_total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discounted_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Add total order value field
    
    
    def save(self, *args, **kwargs):
         if not self.id:
        # Save original address and total value when the order is created
            self.original_street_address = self.address.street_address
            self.original_city = self.address.city
            self.original_state = self.address.state
            self.original_postal_code = self.address.postal_code
            self.original_country = self.address.country
            
      
         super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - Status: {self.status}"
  
    def cancel_order(self):
        # Method to cancel the order
        if self.status == self.PROCESSING:
            # Restock products
            for item in self.items.all():
                item.size.stock += item.quantity
                item.size.save()

            self.status = self.CANCELLED
            self.save()

            if self.payment_status == 'Completed' :
                user_wallet = self.user.wallet
                user_wallet.add_funds(self.discounted_total)
                self.payment_status = 'Refunded'
                self.save()

            return True
        return False


  
    def ship_order(self):
        # Method to cancel the order
        if self.status == self.PROCESSING:
            # Restock products
            
            self.status = self.SHIPPED
            self.save()
            return True

        return False

  
    def deliver_order(self):
        # Method to cancel the order
        if self.status == self.SHIPPED:
            self.status = self.DELIVERED
            self.save()

            if self.payment_status == 'Pending' :
                self.payment_status = 'Completed'
                self.save()
            return True
        return False


    def return_order(self):
        # Method to return the order
        if self.status == self.DELIVERED:
            # Restock products
            for item in self.items.all():
                item.size.stock += item.quantity
                item.size.save()

            self.status = self.RETURNED
            self.save()

            if self.payment_status == self.COMPLETED:
                # Refund the payment if it was completed
                user_wallet = self.user.wallet
                user_wallet.add_funds(self.discounted_total)
                self.payment_status = self.REFUNDED
                self.save()

            return True
        return False


    def get_order_history(self):
        # Method to get order history for the user
        return Order.objects.filter(user=self.user).order_by('-created_at')

    def get_order_status_display(self):
        # Method to get display text for order status
        return dict(self.STATUS_CHOICES)[self.status]
    
    def total_value(self):
        # Method to calculate the total order value
        total_value = sum(item.total_price() for item in self.items.all())
        self.total_value = total_value
        self.save()
        return total_value


from django.core.exceptions import ValidationError

from product.models import Size, Products

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    original_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.quantity} x {self.size.measurement} of {self.product.name} in Order #{self.order.id} - Status: {self.order.status}"

    def total_price(self):
        return self.original_price * self.quantity  # Use original_price for calculations
    

    def save(self, *args, **kwargs):
        # Save the original price when the order item is created
        

        # Calculate the total price before saving
        total_price = self.total_price()

        # Check if there is enough stock to fulfill the order
        if self.size.stock < self.quantity:
            raise ValidationError(f"Insufficient stock for {self.product.name}. Current stock: {self.size.stock}")

        # Update the product stock
        self.size.stock -= self.quantity
        self.size.save()

        super().save(*args, **kwargs)