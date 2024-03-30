import  datetime
from decimal import Decimal
from django.db import models
from django.db.models import CASCADE, PROTECT, SET_NULL
from django.db.models import CASCADE, signals
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver




# Create your models here.

class Products(models.Model):  # Use PascalCase for model names
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Use appropriate max_digits
    tot_price = models.DecimalField(max_digits=15, decimal_places=2,default=10)  # Use appropriate max_digits
    discount = models.IntegerField(verbose_name="Discount Percentage")
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    size = models.IntegerField(default=10,null=True)
    product_rating = models.ForeignKey('Rating', on_delete=CASCADE, null=True)
    Category=models.ForeignKey('Category', on_delete=CASCADE, null=True)
    making_charge = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    daily_rate = models.ForeignKey('DailyRate', on_delete=CASCADE, null=True)
    GST = models.DecimalField(max_digits=15, decimal_places=2,default=10) 
    MC = models.DecimalField(max_digits=15, decimal_places=2,default=10) 
    discprice = models.DecimalField(max_digits=15, decimal_places=2,default=10)

    def __str__(self):
        return self.name
    


    def save(self, *args, **kwargs):
        self.daily_rate = DailyRate.objects.order_by('date').last()
        self.price=(self.daily_rate.rate*(self.weight+(self.making_charge*self.weight)/100))
        self.discprice=(self.daily_rate.rate*(self.weight+((self.making_charge-(self.making_charge*Decimal(self.discount/100)))*self.weight)/100))
        self.GST=int((self.discprice*3)/100)
        self.MC=(self.daily_rate.rate*(self.making_charge*self.weight)/100)
        self.tot_price=int(self.discprice+self.GST)
        super().save(*args, **kwargs)
       
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Rating(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_ratings', default=4)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class Size(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_sizes')
    measurement = models.CharField(max_length=50)  # You can adjust the max_length as needed
    stock = models.IntegerField()


class Image(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    images= models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/')  # Add upload path for images
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_related_products()  # Call after saving

    def update_related_products(self):
        products = Products.objects.filter(Category=self)
        for product in products:
                if self.is_active:
                    pass
                else:
                    product.is_active = self.is_active
                    product.save()



class DailyRate(models.Model):
    rate = models.IntegerField()
    date = models.DateTimeField(auto_now=True)


    



# models.py

from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField()

    def __str__(self):
        return self.title
 

@receiver(signals.post_save, sender=DailyRate)
def update_products_on_daily_rate_change(sender, instance, **kwargs):
    # Update all related products when a new DailyRate is created or updated
    related_products = Products.objects.all()
    for product in related_products:
        product.daily_rate = instance
        product.save()
