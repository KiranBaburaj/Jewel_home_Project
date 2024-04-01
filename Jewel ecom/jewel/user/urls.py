# urls.py
from django.urls import include, path
from .views import add_address,wallet_transaction_history, add_to_cart, return_order,calculate_discounted_total,  cancel_order,  category_product_list, checkout, delete_address, delete_cart_item, edit_address, edit_profile, forget_password, forgot_password, get_messages, logout_view, order_detail, order_history, order_successful, product_detail, resend_otp, reset_password, search_products, signin, signup, update_cart, user_profile, verify_otp,home, verify_otp_forget_password, view_cart
from payments.views import * 


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('', home, name='home'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('signin/', signin, name='signin'),
 path('accounts/profile/', home, name='home'),  # Adjust 'profile_view' with your actual view
     path('accounts/', include('allauth.urls')),
       path('resend-otp/', resend_otp, name='resend_otp'),
      path('category/<int:category_id>/', category_product_list, name='category_product_list'),
          path('logout/',logout_view, name='logout'),
      path('product/<int:product_id>/', product_detail, name='product_detail'),

   path('calculate_discounted_total/', calculate_discounted_total, name='calculate_discounted_total'),  # Add this line
       

         path('user_profile/', user_profile, name='user_profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),

    path('forgot_password/', forgot_password, name='forgot_password'),


 path('add_to_cart/', add_to_cart, name='add_to_cart'),
  path('view_cart/', view_cart, name='view_cart'),
    path('update_cart/', update_cart, name='update_cart'),
    path('delete_cart_item/', delete_cart_item, name='delete_cart_item'),

        path('search/', search_products, name='search_products'),

  path('checkout/', checkout, name='checkout'),
 path('order_successful/<int:order_id>/', order_successful, name='order_successful'),
 path('get_messages/', get_messages, name='get_messages'),

 path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
        path('order/<int:order_id>/return/', return_order, name='return_order'),
    path('order/history/', order_history, name='order_history'),

   
       path('forget-password/', forget_password, name='forget_password'),
    path('verify-otp-forget-password/', verify_otp_forget_password, name='verify_otp_forget_password'),
      path('reset-password/', reset_password, name='reset_password'),

    path('payment_page/<int:order_id>/', payment_page, name='payment_page'),
    path('process_cod_payment/<int:order_id>/', process_cod_payment, name='process_cod_payment'),
    path('process_razorpay_payment/<int:order_id>/', process_razorpay_payment, name='process_razorpay_payment'),
    path('generate-pdf-invoice/<int:order_id>/', generate_invoice_pdf, name='generate_invoice_pdf'),


 path('add_address/', add_address, name='add_address'),
    path('edit_address/<int:address_id>/', edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),
    
    # Add other URLs as needed

     path('process_razorpay_payment/<int:order_id>/', process_razorpay_payment, name='process_razorpay_payment'),
    path('payment_success/<int:order_id>/', payment_success, name='payment_success'),
    path('payment_failure/<int:order_id>/', payment_failure, name='payment_failure'),
        path('product/<int:product_id>/rate/', create_rating, name='create_rating'),
          path('create_reason/<int:order_id>/', create_reason, name='create_reason'),
           path('wallet/transaction-history/', wallet_transaction_history, name='wallet_transaction_history'),
]

