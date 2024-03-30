# payments/urls.py
from django.urls import path
from .views import payment_page, process_cod_payment, process_razorpay_payment,create_rating



urlpatterns = [
    path('payment_page/<int:order_id>/', payment_page, name='payment_page'),
    path('process_cod_payment/<int:order_id>/', process_cod_payment, name='process_cod_payment'),
    path('process_razorpay_payment/<int:order_id>/', process_razorpay_payment, name='process_razorpay_payment'),
    path('product/<int:product_id>/rate/', create_rating, name='create_rating'),
    # Add other payment-related URLs as needed
]
