from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon
from .forms import CouponForm

def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'admin/coupon/coupon_list.html', {'coupons': coupons})

def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.save()
            messages.success(request, 'Coupon created successfully.')
            return redirect('coupon_list')
    else:
        form = CouponForm()
    return render(request, 'admin/coupon/create_coupon.html', {'form': form})

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect('coupon_list')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin/coupon/edit_coupon.html', {'form': form, 'coupon': coupon})

def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully.')
    return redirect('coupon_list')



# views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductOffers, CategoryOffers
from .forms import ProductOfferForm, CategoryOfferForm

def product_offer_create(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = ProductOfferForm()
    return render(request, 'admin/offers/product_offer_create.html', {'form': form})

def product_offer_edit(request, pk):
    offer = get_object_or_404(ProductOffers, pk=pk)
    if request.method == 'POST':
        form = ProductOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = ProductOfferForm(instance=offer)
    return render(request, 'admin/offers/product_offer_edit.html', {'form': form})

def product_offer_delete(request, pk):
    offer = get_object_or_404(ProductOffers, pk=pk)
    offer.delete()
    return redirect('product_offers_list')  # Change 'admin_homepage' to the appropriate URL
  

def category_offer_create(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = CategoryOfferForm()
    return render(request, 'admin/offers/category_offer_create.html', {'form': form})

def category_offer_edit(request, pk):
    offer = get_object_or_404(CategoryOffers, pk=pk)
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL
    else:
        form = CategoryOfferForm(instance=offer)
    return render(request, 'admin/offers/category_offer_edit.html', {'form': form})

def category_offer_delete(request, pk):
    offer = get_object_or_404(CategoryOffers, pk=pk)
    offer.delete()
    return redirect('category_offers_list')  # Change 'admin_homepage' to the appropriate URL



# views.py

from django.shortcuts import render
from .models import ProductOffers, CategoryOffers

def list_product_offers(request):
    # Retrieve all product offers from the database
    product_offers = ProductOffers.objects.all()
    return render(request, 'admin/offers/product_offer_list.html', {'product_offers': product_offers})

def list_category_offers(request):
    # Retrieve all category offers from the database
    category_offers = CategoryOffers.objects.all()
    return render(request, 'admin/offers/category_offer_list.html', {'category_offers': category_offers})


def offers(request):

    return render(request, 'admin/offers/offer.html')





