# urls.py
from django.urls import path
from .views import view_wishlist, add_to_wishlist, remove_from_wishlist

urlpatterns = [
    path('wishlist/', view_wishlist, name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    # Add other URLs as needed
]
