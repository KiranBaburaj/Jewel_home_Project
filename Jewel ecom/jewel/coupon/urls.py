from django.urls import path

from . import views
from .views import coupon_list, create_coupon, edit_coupon, delete_coupon

urlpatterns = [
    path('coupons/', coupon_list, name='coupon_list'),
    path('coupons/create/', create_coupon, name='create_coupon'),
    path('coupons/edit/<int:coupon_id>/', edit_coupon, name='edit_coupon'),
    path('coupons/delete/<int:coupon_id>/', delete_coupon, name='delete_coupon'),
     path('product-offer/create/', views.product_offer_create, name='product_offer_create'),
    path('product-offer/<int:pk>/edit/', views.product_offer_edit, name='product_offer_edit'),
    path('product-offer/<int:pk>/delete/', views.product_offer_delete, name='product_offer_delete'),
    path('product-offers/', views.list_product_offers, name='product_offers_list'),
        path('offers/', views.offers, name='offers'),

    # Category Offer URLs
    path('category-offer/create/', views.category_offer_create, name='category_offer_create'),
    path('category-offer/<int:pk>/edit/', views.category_offer_edit, name='category_offer_edit'),
    path('category-offer/<int:pk>/delete/', views.category_offer_delete, name='category_offer_delete'),
    path('category-offers/', views.list_category_offers, name='category_offers_list'),

]
