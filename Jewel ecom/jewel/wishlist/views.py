# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Wishlist
from product.models import Products  # Import your product model
from django.contrib.auth.decorators import login_required

@login_required(login_url='signin')  # Replace with your actual login URL
def view_wishlist(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    return render(request, 'user/wishlist/wishlist.html', {'wishlist': wishlist})

@login_required(login_url='signin')  # Replace with your actual login URL
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)  # Replace with your actual product model
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wishlist.products.add(product)
    return redirect('product_detail', product_id=product_id)

@login_required(login_url='signin')  # Replace with your actual login URL
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)  # Replace with your actual product model
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wishlist.products.remove(product)
    return redirect('wishlist')
