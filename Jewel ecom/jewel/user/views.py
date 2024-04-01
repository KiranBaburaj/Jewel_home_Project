import os
import random
import string
from datetime import datetime, timedelta
from aiohttp import request
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import render, redirect
from psycopg2 import IntegrityError
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .forms import SignupForm, OTPForm
from .models import User as CustomUser
from product.models import Banner, Products,Category
from django.utils.translation import gettext as _
from twilio.rest import Client


def home(request):
    user = request.user 
        
    products = Products.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    banner = Banner.objects.get(id=1)
    context = {'products': products, 'banner': banner, 'categories': categories}

    # Check if the user is authenticated and modify the context accordingly
    if user.is_authenticated:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        context['authenticated_user'] = user

    return render(request, 'user/home.html', context)


from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from django.shortcuts import redirect

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data.get('password'))
            if user is not None:
                # Check if the user has verified OTP during signup
                if not user.is_verified:
                    form = AuthenticationForm()
                    # Redirect to the OTP verification page
                    return redirect('verify_otp')
                # If OTP is verified, proceed with login
                login(request, user)
                return redirect('home')
            else:
                # Add an error message if authentication fails
                messages.error(request, 'Invalid username or password.')
        else:
            # Add an error message if the form is invalid
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'user/signin.html', {'form': form})


def generate_otp():
    return ''.join(random.choices(string.digits, k=4))

def send_otp_twilio(user):
    account_sid = 'ACe8cae81e087c6c60d31751fd56d7fd99'
    auth_token = '810ec3b03b749fbeb6faf4095362e2b8'
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=f"Your OTP is {user.otp}",
            from_='+19402455707',
            to=user.phone_number
        )
        print(f"Message SID: {message.sid}")
    except TwilioRestException as e:
        print(f"Twilio error: {e}")
from django.contrib import messages
from django.contrib import messages
from django.contrib import messages
from coupon.models import CategoryOffers, ProductOffers, ReferralCoupon

# views.py

from django.db import IntegrityError
from django.contrib import messages

def generate_referral_code():
    # Generate a random 6-character alphanumeric code
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                messages.error(request, 'This phone number is already in use. Please use a different phone number.')
                return render(request, 'user/signup.html', {'form': form})

            referral_coupon_code = form.cleaned_data.get('referral_coupon_code')
            if referral_coupon_code:
                    try:
                        # Retrieve the referral coupon
                        old_user = ReferralCoupon.objects.get(coupon_code=referral_coupon_code).user
                        old_user_wallet, _ = Wallet.objects.get_or_create(user=old_user)
                        old_user_ReferralCoupon = ReferralCoupon.objects.get(user=old_user)
                        old_user_wallet.add_funds(100)
                        # Increase the number of referrals made by the user
                        old_user_ReferralCoupon.referrals_made += 1
                        # Set the is_used status to true
                        old_user_ReferralCoupon.is_used = True
                        old_user_wallet.save()
                        old_user_ReferralCoupon.save()

                    except ReferralCoupon.DoesNotExist:
                        messages.error(request, 'Invalid referral coupon code. Please try again.')


            referral_code = generate_referral_code()
            referral_coupon = ReferralCoupon.objects.create(user=user, coupon_code=referral_code)
      

            user.otp = generate_otp()
            user.otp_generated_at = datetime.now() + timedelta(minutes=1)
            user.save()

            # Store the user's primary key in the session for OTP verification
            request.session['user_id_for_otp_verification'] = user.id

            # Send OTP and redirect to OTP verification page
            send_otp_twilio(user)
            return redirect('verify_otp')
        else:
            print(f"Form errors: {form.errors}")
            # Optionally, you can add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignupForm()

    return render(request, 'user/signup.html', {'form': form})

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from payments.models import Transaction


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def wallet_transaction_history(request):
    # Retrieve the current user's wallet
    user_wallet = Wallet.objects.get(user=request.user)
    
    # Retrieve the initial balance of the wallet
    initial_balance = user_wallet.balance
    
    # Retrieve the wallet transaction history
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(transactions, 10)  # 10 transactions per page
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)
    
    # Calculate the opening balance
    opening_balance = initial_balance
    for transaction in transactions:
        if transaction.transaction_type == 'credit':
            opening_balance -= transaction.amount
        elif transaction.transaction_type == 'debit':
            opening_balance += transaction.amount
    
    # Render the template with the wallet transaction history, opening balance, and current balance
    return render(request, 'user/user/wallet_transaction.html', {'transactions': transactions, 'opening_balance': opening_balance, 'current_balance': user_wallet.balance})


def verify_otp(request):
    print("Entering verify_otp view")
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            print(f"Entered OTP: {otp}")

            # Retrieve the user ID from the session using the correct key
            user_id = request.session.get('user_id_for_otp_verification')

            if user_id is None:
                messages.error(request, _('User not found in session'))
                print("User not found in session")
                return redirect('verify_otp')

            # Retrieve the user using the user ID
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                messages.error(request, _('User not found'))
                return redirect('verify_otp')

            print(f"Stored OTP: {user.otp}, Entered OTP: {otp}")

            if str(user.otp) == otp:  # Convert user.otp to string for comparison
                user.is_verified = True
                user.save()
                login(request, user)
                # Clear the user ID from the session after successful verification
                request.session.pop('user_id_for_otp_verification', None)
                print("OTP verification successful")
                return redirect('home')
            else:
                messages.error(request, _('Invalid OTP or OTP has expired'))
                print("OTP validation failed")
    else:
        form = OTPForm()

    return render(request, 'user/verify_otp.html', {'form': form})

# Import necessary modules
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


def resend_otp(request):
    # Retrieve the user ID from the session
    user_id = request.session.get('user_id_for_otp_verification')

    if user_id is None:
        return JsonResponse({'status': 'error', 'message': 'User not found in session'})

    # Retrieve the user using the user ID
    try:
        user = CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})

    # Generate a new OTP and update the user's OTP and OTP generation time
    user.otp = generate_otp()
    user.otp_generated_at = datetime.now() + timedelta(minutes=1)
    user.save()

    # Resend the new OTP
    send_otp_twilio(user)

    return JsonResponse({'status': 'success', 'message': 'OTP resent successfully'})

# views.py



from django.contrib.auth import get_user_model, login

from .forms import ForgetPasswordForm, OTPForm
from .utils import generate_otp, send_otp_email

User = get_user_model()

def forget_password(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                # Generate OTP and update user's OTP and OTP generation time
                user.otp = generate_otp()
                user.otp_generated_at = timezone.now() + timedelta(minutes=5)
                user.save()

                # Send OTP via Twilio (SMS)
                send_otp_twilio(user)

                # Send OTP via email
                send_otp_email(user)

                # Store user ID in session for OTP verification
                request.session['user_id_for_otp_verification'] = user.id

                # Redirect to OTP verification page
                return redirect('verify_otp_forget_password')
            else:
                messages.error(request, 'User not found. Please enter a valid email or phone number.')
    else:
        form = ForgetPasswordForm()

    return render(request, 'user/user/forget_password.html', {'form': form})


def verify_otp_forget_password(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']

            # Retrieve user ID from session
            user_id = request.session.get('user_id_for_otp_verification')

            if user_id is None:
                messages.error(request, 'User not found in session')
                return redirect('verify_otp_forget_password')

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, 'User not found')
                return redirect('verify_otp_forget_password')

            if str(user.otp) == otp and user.otp_generated_at > timezone.now():
                # Clear user ID from session
                request.session.pop('user_id_for_otp_verification', None)
                login(request, user)
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP or OTP has expired. Please try again.')

    else:
        form = OTPForm()

    return render(request, 'user/user/verify_otp_forget_password.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash



@login_required(login_url='signin')
def reset_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('home')  # Redirect to the home page or any other desired page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'user/user/reset_password.html', {'form': form})

# In utils.py

import random
import string
from twilio.rest import Client
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user):
    subject = 'OTP for Password Reset'
    message = f'Your OTP for password reset is {user.otp}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


from django.db.models import Avg

def category_product_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Products.objects.filter(Category=category, is_active=True)
    
    for product in products:
        average_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.average_rating = round(average_rating, 1) if average_rating else None
    
    context = {
        'category': category,
        'products': products,
    }
    
    return render(request, 'user/category_product_list.html', context)


from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from product.models import Products
from django.db.models import Avg,Sum


def product_detail(request, product_id):
    product = get_object_or_404(Products, pk=product_id, is_active=True)
    related_products = Products.objects.filter(Category=product.Category, is_active=True).exclude(pk=product_id)
    random_related_products = random.sample(list(related_products), min(3, len(related_products)))
    ratings_reviews = Rating.objects.filter(product_id=product_id)
    average_rating = Rating.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']

    product_offers = ProductOffers.objects.filter(
        product=product,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    disc = 0
    if product_offers.exists():
        disc =round((product.MC * product_offers[0].discount_percentage) / 100, 0)



    
    # Retrieve active category offers for the displayed product's category
    category_offers = CategoryOffers.objects.filter(
        category=product.Category,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    discc = 0
    if category_offers.exists():
        discc = round(product.MC/100 * category_offers[0].discount_percentage ,0) # Assuming you only expect one offer

    success_message = messages.get_messages(request)
    tot=round(product.tot_price-(discc+disc ),0)

    context = {
        'ratings_reviews': ratings_reviews,
        'product': product,
        'random_related_products': random_related_products,
        'success_message': success_message,
        'average_rating': average_rating,'disc':disc,'discc':discc,'tot':tot,
    }

    return render(request, 'user/product_detail.html', context)



def get_messages(request):
    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'message': message.message,
            'tags': message.tags,
        })

    return JsonResponse({'messages': message_list})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    # Redirect to the home page or any other page after logout
    return redirect('home')

# user/views.py

from .forms import UserProfileForm, ForgotPasswordForm


from .forms import AddressForm
from .models import Address

@login_required(login_url='signin')
def user_profile(request):
    addresses = request.user.addresses.all()
    wallet_balance = request.user.wallet.balance
    try:
        referral_coupon = ReferralCoupon.objects.get(user=request.user)
        referral_coupon_code = referral_coupon.coupon_code
    except ReferralCoupon.DoesNotExist:
        referral_coupon_code = None

    return render(request, 'user/user/user_profile.html', {'referral_coupon_code': referral_coupon_code,'addresses': addresses, 'wallet_balance': wallet_balance})

@login_required(login_url='signin')
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('user_profile')
    else:
        form = AddressForm()
    return render(request, 'user/user/address_form.html', {'form': form})

@login_required(login_url='signin')
def edit_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'user/user/address_form.html', {'form': form})

@login_required
def delete_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    address.delete()
    return redirect('user_profile')


from .forms import UserProfileForm

def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
  
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'user/user/edit_profile.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # Logic to handle forgot password
            messages.success(request, 'Password reset instructions sent to your email.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'user/user/forgot_password.html', {'form': form})



from django.http import JsonResponse
from .models import Products, Size, Cart, CartItem
from payments.models import Wallet,Rating

from django.contrib.auth.decorators import login_required


@login_required(login_url='signin')
def add_to_cart(request):
    if request.method == 'POST':
        try:
            
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            product_id = request.POST.get('product_id')
            size_id = request.POST.get('size')
            quantity = int(request.POST.get('quantity', 1))

            product = get_object_or_404(Products, pk=product_id)
            size = get_object_or_404(Size, pk=size_id)

            
            product_offers = ProductOffers.objects.filter(
                product=product,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
                )
            disc = 0
            if product_offers.exists():
                disc = (product.MC/100) * product_offers[0].discount_percentage



    
            # Retrieve active category offers for the displayed product's category
            category_offers = CategoryOffers.objects.filter(
                category=product.Category,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )

            discc = 0
            if category_offers.exists():
                discc = product.MC/100 * category_offers[0].discount_percentage  # Assuming you only expect one offer

            
            tot=product.tot_price-(discc+disc )


            cart, _ = Cart.objects.get_or_create(user=request.user)

            existing_item = CartItem.objects.filter(cart=cart, product=product, size=size).first()
            
            

            if existing_item:
                existing_item.quantity += quantity
                existing_item.save()
                messages.success(request, f"{quantity} {product.name} added to the cart.")
            else:
                if size.stock < quantity:
                    messages.error(request, f"Insufficient stock for {product.name}. Current stock: {size.stock}")
                else:
                    new_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        size=size,
                        quantity=quantity,offer_price=tot,
                    )
                    messages.success(request, f"{quantity} {product.name} added to the cart.")

            return JsonResponse({'success': True, 'message': 'Added to cart.'})

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return JsonResponse({'success': False, 'message': error_message})

    return JsonResponse({'success': False, 'message': "Invalid request."})




@login_required(login_url='signin')
def view_cart(request):
    # Get the user's cart
    
    user_cart = Cart.objects.get(user=request.user)
    print(f"User Cart: {user_cart}")

    # Get cart items
    cart_items = user_cart.items.all()
    print(f"Cart Items: {cart_items}")

    total_cart_value = round(user_cart.total_cart_value(),0)

    context = {
        'cart_items': cart_items,'total_cart_value': total_cart_value,
    }

    return render(request, 'user/cart/view_cart.html', context)

from django.shortcuts import redirect

@login_required(login_url='signin')
def update_cart(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_')[1]
                quantity = int(value)
                cart_item = get_object_or_404(CartItem, id=item_id)
                try:
                    cart_item.quantity = quantity
                    cart_item.save()
                except ValidationError as e:
                    messages.error(request, e.message)
        return redirect('view_cart')  # Redirect back to the cart page
    else:
        return redirect('view_cart')  # Handle GET requests similarly






def delete_cart_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        # Check if the item belongs to the current user's cart before deleting
        if cart_item.cart.user == request.user:
            cart_item.delete()
            messages.success(request, 'Item removed from the cart.')
        else:
            messages.error(request, 'Invalid request.')

    return redirect('view_cart')





from .forms import SearchForm


def search_products(request):
    form = SearchForm(request.GET)
    
    # Fetch all products initially
    products = Products.objects.filter(is_active=True).annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating')  
    
    # Handle search query
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            products = products.annotate(avg_rating=Avg('rating__rating')).filter(name__icontains=search_query)

        sort_by = form.cleaned_data.get('sort_by')
        if sort_by == 'popularity':
            products = products.annotate(total_quantity_sold=Sum('product_sizes__orderitem__quantity')).exclude(total_quantity_sold=None).order_by('-total_quantity_sold')  # Assuming there's a related product_rating field
        elif sort_by == 'price_low_high':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('price')
        elif sort_by == 'price_high_low':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('-price')
        elif sort_by == 'average_ratings':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating')         
        elif sort_by == 'featured':
            # Add logic for featured sorting
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('-avg_rating') 
        elif sort_by == 'new_arrivals':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('created_at')
        elif sort_by == 'a_to_z':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('name')
        elif sort_by == 'z_to_a':
            products = products.annotate(avg_rating=Avg('rating__rating')).order_by('-name')
        # Add more sorting options as needed

    context = {
        'form': form,
        'products': products,
    }

    return render(request, 'user/search_results.html', context)



import razorpay 

from .models import Address, Order, OrderItem
from user.models import Cart

from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from coupon.models import Coupon
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from decimal import Decimal

from decimal import Decimal
from django.shortcuts import redirect


@csrf_protect
@login_required(login_url='signin')
def checkout(request):
    user_addresses = Address.objects.filter(user=request.user)
    user_cart = Cart.objects.get(user=request.user)
    total_cart_value = user_cart.total_cart_value()
    applicable_coupons = []
    discounted_total = None
    delivery_charge = 0  
    razor=0

    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        selected_address = Address.objects.get(id=selected_address_id)
        selected_coupon_code = request.POST.get('coupon_code', None)


        # Fetch wallet object associated with the user
        wallet = Wallet.objects.get(user=request.user)
        payment_status = 'Pending'

        # Check if the cart has items before creating the order
        if user_cart.items.exists():
            order_amount = int(user_cart.total_cart_value() * 100)  # Convert to paise
            original_total_value = order_amount
            discount=0
            # Apply coupon discount if a coupon is selected
            if selected_coupon_code:
                coupon = Coupon.objects.filter(
                    code=selected_coupon_code,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_until__gte=timezone.now(),
                    minimum_purchase_amount__lte=user_cart.total_cart_value()
                ).first()
                if coupon:
                    order_amount /= 100  # Convert back to the original currency unit (INR)
                    discounted_total =round( coupon.calculate_discounted_total(
                        coupon.discount_type,
                        order_amount,
                        coupon.discount_amount,
                        coupon.discount_percentage
                    ),0)
                    discount=int(user_cart.total_cart_value())-discounted_total
                    
                    # Update the order_amount with the discounted_total
                    original_total_value = order_amount
                    order_amount = max(0, discounted_total * 100)  # Convert to paise
                    if discounted_total < 5000:
                            delivery_charge = 100
                            order_amount += delivery_charge*100
                            original_total_value += delivery_charge 
                            discounted_total += delivery_charge              

                    # Set the discounted total in the correct unit (INR)
                    discounted_total = Decimal(discounted_total)
            else:
                discounted_total =round( original_total_value/100,0)
                if discounted_total < 5000 :
                            delivery_charge = 100
                            order_amount += delivery_charge*100
                            original_total_value += delivery_charge 
                            discounted_total += delivery_charge     
                
                
            # Check wallet balance
            if wallet.balance >= order_amount / 100:  # Convert order amount back to currency unit (INR)
                # Deduct order amount from wallet balance
                order_amount_decimal = Decimal(order_amount) / Decimal(100)
                wallets=order_amount_decimal
                wallet.deduct_funds(order_amount_decimal)
                payment_method = 'Wallet'
                payment_status = 'Completed'
            elif wallet.balance > 0:
                # Deduct available wallet balance
              
                # Calculate remaining amount to be paid using Razorpay
                remaining_amount = (order_amount / 100) - float(wallet.balance)
                wallets=wallet.balance
                wallet.deduct_funds(wallet.balance)
                razor=remaining_amount
                order_amount = remaining_amount*100

                payment_method = 'WalletandRazorpay'
           
            else :
                wallets=0
                payment_method = 'Razorpay'
                razor=order_amount/100

            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            razorpay_order = razorpay_client.order.create({
                'amount': order_amount,
                'currency': 'INR',
                'receipt': f'order_{user_cart.id}',
            })
            razorpay_order_id = razorpay_order['id']
            # Create a new order
            new_order = Order.objects.create(
                razorpay_order_id=razorpay_order_id,
                user=request.user,
                address=selected_address,
                original_total_value=original_total_value,
                discounted_total=round(discounted_total,0),
                payment_method=payment_method,
                payment_status=payment_status,
                wallet=wallets,razor=razor,
                coupon_code=selected_coupon_code,
                coupon_discount = discount,
                delivery_charge=round(delivery_charge,0),

            )
            
            # Copy items from the user's cart to the order
            for cart_item in user_cart.items.all():
                OrderItem.objects.create(
                    order=new_order,
                    product=cart_item.product,
                    size=cart_item.size,
                    quantity=cart_item.quantity,
                    original_price=cart_item.offer_price,
                )

            # Clear the user's cart after creating the order
            user_cart.items.all().delete()

            if new_order.payment_status=='Completed':
                return redirect('order_successful', order_id=new_order.id)



            # Redirect to the order successful page with order ID
            return redirect('payment_page', order_id=new_order.id)

        else:
            messages.warning(request, "Your cart is empty. Add items before checking out.")

    # Get applicable coupons for the user
    applicable_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now(),
        minimum_purchase_amount__lte=user_cart.total_cart_value()
    )

    context = {
        'user_addresses': user_addresses,
        'user_cart': user_cart,
        'applicable_coupons': applicable_coupons,
        'discounted_total': discounted_total,'total_cart_value' : total_cart_value ,'delivery_charge':delivery_charge,
    }

    return render(request, 'user/order/checkout.html', context)

def calculate_discounted_total(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        coupon_code = request.GET.get('coupon_code')
        total_cart_value = float(request.GET.get('total_cart_value'))

        print(f"Received coupon_code: {coupon_code}, total_cart_value: {total_cart_value}")

        # Check if the cart has items before calculating the discount
        if total_cart_value > 0 and coupon_code:
            coupon = Coupon.objects.filter(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now(),
                minimum_purchase_amount__lte=total_cart_value
            ).first()
            if coupon:
                discounted_total = coupon.calculate_discounted_total(
                    coupon.discount_type,
                    total_cart_value,
                    coupon.discount_amount,
                    coupon.discount_percentage
                )
                print(f"Calculated discounted_total: {discounted_total}")
                return JsonResponse({'discounted_total': discounted_total})

    return JsonResponse({'discounted_total': 0})

def order_successful(request, order_id):
    # Retrieve the order based on the order_id
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }

    return render(request, 'user/order/order_successful.html', context)




def order_detail(request, order_id):
    order = Order.objects.get(pk=order_id)
    return render(request, 'user/order/order_detail.html', {'order': order})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    order.cancel_order()
    messages.success(request, f'Order #{order.id} has been canceled successfully.')
    return redirect('order_detail', order_id=order.id)


def return_order(request, order_id):
    # Get the order object
    order = get_object_or_404(Order, id=order_id)
    # Call the return_order method on the order object
    if order.return_order():
        messages.success(request, f'Order #{order.id} has been returned successfully.')
    else:
        messages.error(request, f'Unable to return Order #{order.id}.')
    # Redirect to the order detail page
    return redirect('order_detail', order_id=order.id)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)  # 10 orders per page
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    return render(request, 'user/order/order_history.html', {'orders': orders})

