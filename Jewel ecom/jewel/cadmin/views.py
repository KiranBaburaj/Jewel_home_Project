from django.conf import settings
from django.contrib.auth import authenticate, login as adlogin
from django.contrib.auth import authenticate, logout as adlogout
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from user.models import Order, User
from .forms import RegisterUser,EditForm,DailyRateForm, SizeForm, SizeFormSet
from django.contrib import messages
from product.models import Products, Size
from .forms import ProductForm
from django.contrib.auth.decorators import login_required  # Assuming login is required
from .forms import ProductForm, ImageForm
from django.forms import inlineformset_factory


@never_cache
def superuser_login(request):
    if request.user.is_authenticated:
        return redirect('custom_admin_homepage')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            adlogin(request, user)
            # Redirect to the custom admin panel homepage
            return redirect('custom_admin_homepage')
        else:
            # Display invalid login error
            error_message = 'Invalid username or password.'
            return render(request, 'admin/superuser_login.html', {'error_message': error_message})
    else:
        return render(request, 'admin/superuser_login.html')


@login_required(login_url='superuser_login')  # Apply login_required if needed
def create_user(request):
    if request.method == "POST":
        form = RegisterUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully!")
            return redirect('user_list')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterUser()
    return render(request, "create_user.html", {'form': form})


@never_cache
@login_required(login_url='superuser_login')
def user_list(request):
    users = User.objects.all()  
    context = {'users': users}
    return render(request, 'admin/userdetail/user_list.html', context)

    
@never_cache
@login_required(login_url='superuser_login')
def search_users(request):
    # Same logic as the user_list function, but with a different name
    query = request.GET.get('query')
    print(query)
    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()

    context = {'users': users}
    return render(request, 'admin/userdetail/user_list.html', context)


@never_cache
@login_required(login_url='superuser_login')
def edit_user(request, user_id):
    request.session.pop('_messages', None)

    user = get_object_or_404(User, id=user_id)
    form=EditForm(instance=user)
    
    if request.method=="POST":
        form=EditForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,"")
            return redirect('user_list')
        else:
            messages.error(request,form.errors)
            form=EditForm(instance=user)

            return render(request,'edit_user.html',{'form':form})
    return render(request,'edit_user.html',{'form':form})

    """if request.method == 'POST':
        # Handle form data
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        

        user.save()
        return redirect('user_list')  # Redirect to user list upon success
    
    else:
        # Render the edit form for GET requests
        context = {'user': user}
        return render(request, 'edit_user.html', context)"""


# user/views.py
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect

User = get_user_model()

def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('user_list')

def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_list')


@never_cache
@login_required(login_url='superuser_login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')  # Redirect to user list
    else:
        context = {'user': user}
        return render(request, 'delete_user.html', context)


@never_cache
@login_required(login_url='superuser_login')
def adlogout_view(request):
    adlogout(request)
    return redirect('superuser_login')  # Redirect to your login page after logout
from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@never_cache
@login_required(login_url='superuser_login')
def products_list(request):
    # Assuming you have 10 products per page, adjust as needed
    products_per_page = 10

    products = Products.objects.all().order_by('-is_active', 'name')
    paginator = Paginator(products, products_per_page)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page.
        products = paginator.page(paginator.num_pages)

    context = {'products': products}

    return render(request, 'admin/product/prod_list.html', context)


from .forms import ProductForm, ImageFormSet


@never_cache
@login_required(login_url='superuser_login')
def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        size_formset = SizeFormSet(request.POST, queryset=Size.objects.none())

        if product_form.is_valid() and image_formset.is_valid() and size_formset.is_valid():
            product = product_form.save(commit=False)
            category_id = request.POST.get('Category')
            category = Category.objects.get(pk=category_id)
            product.Category = category
            product.save()

            for form in image_formset:
                if form.cleaned_data:
                    image = form.cleaned_data['images']
                    photo = Image(product=product, images=image)
                    photo.save()

            for form in size_formset:
                if form.cleaned_data:
                    size = form.cleaned_data['measurement']
                    stock = form.cleaned_data['stock']
                    product_size = Size(product=product, measurement=size, stock=stock)
                    product_size.save()

            return redirect('products_list')
    else:
        product_form = ProductForm()
        image_formset = ImageFormSet(queryset=Image.objects.none())
        size_formset = SizeFormSet(queryset=Size.objects.none())

    categories = Category.objects.all()

    return render(request, 'admin/product/create_product.html', {
        'product_form': product_form,
        'image_formset': image_formset,
        'size_formset': size_formset,
        'categories': categories,
    })



@never_cache
@login_required(login_url='superuser_login')
def product_edit(request, pk):
    product = get_object_or_404(Products, pk=pk)
    ImageFormSet = inlineformset_factory(Products, Image, form=ImageForm, extra=3, can_delete=True)
    SizeFormSet = inlineformset_factory(Products, Size, form=SizeForm, extra=3, can_delete=True)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ImageFormSet(request.POST, request.FILES, instance=product)
        size_formset = SizeFormSet(request.POST, instance=product)

        if form.is_valid() and formset.is_valid() and size_formset.is_valid():
            form.save()
            formset.save()
            size_formset.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
        formset = ImageFormSet(instance=product)
        size_formset = SizeFormSet(instance=product)

    return render(
        request,
        'admin/product/product_edit.html',
        {'form': form, 'formset': formset, 'size_formset': size_formset, 'product': product}
    )

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from product.models import Products


@never_cache
@login_required(login_url='superuser_login')
def product_detailad(request, product_pk):
    product = get_object_or_404(Products, pk=product_pk)

    product_offer = product.offer if hasattr(product, 'offer') else None
    category_offers = product.Category.offer if hasattr(product.Category, 'offer') else None
    
    context = {
        'product': product,
        'product_offer': product_offer,
        'category_offers': category_offers,
        # Add other context variables as needed (e.g., related products, reviews)
    }

    return render(request, 'admin/product/product_detail.html', context)

from django.shortcuts import render
from product.models import Category,Image
from .forms import CategoryForm  



@never_cache
@login_required(login_url='superuser_login')
def viewcategory(request):
    categories = Category.objects.all()
    context = {'cate': categories}
    return render(request, 'admin/category/viewcategory.html', context)


@never_cache
@login_required(login_url='superuser_login')
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('viewcategory')
        else:
            pass
            # Handle form errors
    else:
        form = CategoryForm()
    context = {'form': form}
    return render(request, 'admin/category/create_category.html', context)




@never_cache
@login_required(login_url='superuser_login')
def category_detailad(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    # Optionally fetch related products:
    products = Products.objects.filter(Category=category)
    context = {'category': category, 'products': products}
    return render(request, 'admin/category/category_detail.html', context)



from .forms import EditCategoryForm  # Assuming you have a form for editing



@never_cache
@login_required(login_url='superuser_login')
def edit_category(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)

    if request.method == 'POST':
        form = EditCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_detailad', category_pk)
    else:
        form = EditCategoryForm(instance=category)

    context = {'form': form}
    return render(request, 'admin/category/edit_category.html', context)


from django.shortcuts import redirect


@never_cache
@login_required(login_url='superuser_login')
def soft_delete_category(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    category.is_active = False
    category.save()
    return redirect('viewcategory')  # Redirect to category list page


@never_cache
@login_required(login_url='superuser_login')
def product_delete(request, product_pk):
    product = get_object_or_404(Products, pk=product_pk)
    product.is_active=False()
    return redirect('products_list')  
        

@never_cache
@login_required(login_url='superuser_login')
def soft_delete_product(request, product_pk):
    Product = get_object_or_404(Products, pk=product_pk)
    Product.is_active = False
    Product.save()
    return redirect('products_list')  # Redirect to category list page



from product.models import DailyRate
from django.contrib.auth.decorators import login_required  # Assuming login is required


@never_cache
@login_required(login_url='superuser_login')
def create_gold_rate(request):
    if request.method == 'POST':
        form = DailyRateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gold_rate_list')  # Redirect to list view
    else:
        form = DailyRateForm()

    return render(request, 'admin/goldrate/create_gold_rate.html', {'form': form})



@never_cache
@login_required(login_url='superuser_login')
def gold_rate_list(request):
    # Get all gold rates, possibly with filters depending on your needs
    rates = DailyRate.objects.all().order_by('-date')

    return render(request, 'admin/goldrate/gold_rate_list.html', {'rates': rates})

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from product.models import Banner
from .forms import BannerForm  # Create a forms.py file to handle forms

def banner_list(request):
    banners = Banner.objects.all()
    return render(request, 'admin/banner/banner_list.html', {'banners': banners})

def banner_detail(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    return render(request, 'admin/banner/banner_detail.html', {'banner': banner})

def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('banner_list')
    else:
        form = BannerForm()
    return render(request, 'admin/banner/banner_form.html', {'form': form, 'action': 'Create'})

def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            return redirect('banner_list')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'admin/banner/banner_form.html', {'form': form, 'action': 'Edit'})

def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        return redirect('banner_list')
    return render(request, 'admin/banner/banner_confirm_delete.html', {'banner': banner})



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@never_cache
@login_required(login_url='superuser_login')
def admin_order_list(request):
    # Assuming you have a queryset named 'orders'
    orders = Order.objects.all().order_by('-created_at')

    # Number of orders to display per page
    items_per_page = 10

    # Create a Paginator instance
    paginator = Paginator(orders, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the corresponding page from the Paginator
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver the last page
        orders = paginator.page(paginator.num_pages)

    return render(request, 'admin/order/order_list.html', {'orders': orders})

@never_cache
@login_required(login_url='superuser_login')
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/order/order_detail.html', {'order': order})

@never_cache
@login_required(login_url='superuser_login')
def admin_change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('new_status')

    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {new_status}")
    else:
        messages.error(request, "Invalid order status")

    return redirect('admin_order_detail', order_id=order.id)
    

@never_cache
@login_required(login_url='superuser_login')
def admin_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.cancel_order():
        messages.success(request, f"Order #{order.id} has been canceled")
    else:
        messages.error(request, f"Unable to cancel order #{order.id}")

    return redirect('admin_order_detail', order_id=order.id)



@never_cache
@login_required(login_url='superuser_login')
def admin_ship_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.ship_order():
        messages.success(request, f"Order #{order.id} has been shipped")
    else:
        messages.error(request, f"Unable to ship order #{order.id}")

    return redirect('admin_order_detail', order_id=order.id)

@never_cache
@login_required(login_url='superuser_login')
def admin_deliver_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.deliver_order():
        messages.success(request, f"Order #{order.id} has been delivered")
    else:
        messages.error(request, f"Unable to deliver order ship first #{order.id}")

    return redirect('admin_order_detail', order_id=order.id)


from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum

from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum

import csv
from xhtml2pdf import pisa

from datetime import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q



def generate_sales_report_data(period, start_date=None, end_date=None):
    today = timezone.now().date()
    orders = Order.objects.none()

    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == 'custom' and start_date and end_date:
        # Parse start_date and end_date if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # Check if start_date is before end_date
 

    orders = Order.objects.filter(created_at__date__range=[start_date, end_date]).order_by('-created_at')



    droporders = Order.objects.filter(    Q(status='Returned') | Q(status='Cancelled'),
               created_at__date__range=[start_date, end_date] )


    total_sales = orders.aggregate(total_sales=Sum('original_total_value'))['total_sales'] or 0
    total_drop_sales = droporders.aggregate(total_drop_sales=Sum('discounted_total'))['total_drop_sales'] or 0
    total_discount = orders.aggregate(total_discount=Sum('discounted_total'))['total_discount'] or 0
    total_coupons = orders.aggregate(total_coupons=Sum('coupon_discount'))['total_coupons'] or 0
    net_sales = total_sales - total_coupons-total_drop_sales

    return {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'total_coupons': total_coupons,
        'net_sales': net_sales,
        'orders': orders,'total_drop_sales':total_drop_sales
    }


from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def sales_report(request, period=None):
    if request.method == 'POST':
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        try:
            context = generate_sales_report_data(period, start_date, end_date)
            sales_data = context.get('sales_data', [])
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
    else:
        if period not in ['daily', 'weekly', 'monthly', 'yearly', 'custom']:
            period = 'daily'
        context = generate_sales_report_data(period)
        sales_data = context.get('sales_data', [])
   
    return render(request, 'admin/sales_report.html', context)




def render_sales_report_pdf(report_data):
    html = render_to_string('sales_report_pdf.html', report_data)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def render_sales_report_excel(report_data):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Total Value', 'Discount', 'Net Value', 'Created At'])
    for order in report_data['orders']:
        writer.writerow([
            order.id,
            order.user.get_full_name(),
            order.original_total_value,
            order.discounted_total,
     
            order.created_at
        ])

    return response

    
from django.shortcuts import redirect
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest

def download_sales_report_pdf(request, period=None):
    if request.method == 'POST':
        period = request.POST.get('period')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    else:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

    # Validate if both start_date and end_date are provided
    if period == 'custom' and (not start_date or not end_date):
        return HttpResponseBadRequest('Missing start_date or end_date parameters for custom period')

    # Generate report data based on the period and dates
    report_data = generate_sales_report_data(period, start_date, end_date)
    
    # Debug print statements for start_date and end_date
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # Check if period parameter is missing in report_data
    if not report_data.get('period'):
        return HttpResponseBadRequest('Missing period parameter in report data')

    # Render the PDF report using the generated data
    return render_sales_report_pdf(report_data)


def sales_report_excel(request, period=None):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_data = generate_sales_report_data(period, start_date, end_date)
    return render_sales_report_excel(report_data)



from django.shortcuts import render
from datetime import datetime, timedelta
import calendar
import os
from django.conf import settings
from user.models import  OrderItem
import plotly.graph_objs as go
from django.shortcuts import render
from django.db.models import Sum, Q
from datetime import datetime, timedelta
import calendar


@never_cache
@login_required(login_url='superuser_login')
def custom_admin_homepage(request):
    # Define default filter period (monthly)
    filter_period = 'monthly'
    best_selling_products = Products.objects.annotate(total_quantity_sold=Sum('product_sizes__orderitem__quantity')).exclude(total_quantity_sold=None).order_by('-total_quantity_sold')[:10]
    best_selling_categories = Category.objects.annotate(total_quantity_sold=Sum('products__product_sizes__orderitem__quantity')).exclude(total_quantity_sold=None).order_by('-total_quantity_sold')[:10]

    if 'period' in request.GET:
        filter_period = request.GET['period']

    end_date = datetime.now().date()
    if filter_period == 'weekly':
        start_date = end_date - timedelta(days=7)
    elif filter_period == 'monthly':
        # Start from the first day of the current month
        start_date = end_date.replace(day=1)
    elif filter_period == 'yearly':
        # Start from the first day of the current year
        start_date = end_date.replace(day=1, month=1)
    
    # Create a list of dates for the entire filter period
    if filter_period == 'weekly':
        date_range = [start_date + timedelta(days=i) for i in range(7)]
    elif filter_period == 'monthly':
        _, last_day = calendar.monthrange(start_date.year, start_date.month)
        date_range = [start_date.replace(day=1) + timedelta(days=i) for i in range(last_day)]
    elif filter_period == 'yearly':
        date_range = [start_date.replace(month=i, day=1) for i in range(1, 13)]

    # Retrieve sales data from the database based on the filter period
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    droporders = Order.objects.filter(Q(status='Returned') | Q(status='Cancelled'), created_at__date__range=[start_date, end_date])
    total_sales = orders.aggregate(total_sales=Sum('original_total_value'))['total_sales'] or 0
    total_drop_sales = droporders.aggregate(total_drop_sales=Sum('discounted_total'))['total_drop_sales'] or 0
    total_discount = orders.aggregate(total_discount=Sum('discounted_total'))['total_discount'] or 0
    total_coupons = orders.aggregate(total_coupons=Sum('coupon_discount'))['total_coupons'] or 0
    net_sales = total_sales - total_coupons - total_drop_sales
    
    # Extract order dates and total values
    order_dates = [order.created_at.date() for order in orders]
    sales_data = {date: sum(order.discounted_total if order.discounted_total is not None else 0 for order in orders if order.created_at.date() == date) for date in date_range}

    # Calculate monthly total sales for the yearly view
    monthly_total_sales = {}
    monthly_total_count = {}
    if filter_period == 'yearly':
        for month in range(1, 13):
            month_orders = [order for order in orders if order.created_at.month == month]
            month_sales = sum(order.discounted_total if order.discounted_total is not None else 0 for order in month_orders)
            month_count = sum(1 for order in month_orders)
            monthly_total_sales[month] = month_sales
            monthly_total_count[month] = month_count

    # Sort sales data by date
    sorted_sales_data = sorted(sales_data.items())

    # Extract sorted dates and total values
    sorted_dates = [date for date, _ in sorted_sales_data]
    sorted_total_values = [value for _, value in sorted_sales_data]

    # Generate the sales chart
    if filter_period == 'yearly':
        fig = go.Figure(data=go.Scatter(x=list(monthly_total_sales.keys()), y=list(monthly_total_sales.values()), mode='lines+markers'))
    else:
        fig = go.Figure(data=go.Scatter(x=sorted_dates, y=sorted_total_values, mode='lines+markers'))

    fig.update_layout(title=f'Sales Chart ({filter_period.capitalize()})', xaxis_title='Date', yaxis_title='Total Sales', xaxis=dict(tickangle=45))
    chart_div = fig.to_html(full_html=False)

    # Generate the order count chart using Plotly
    if filter_period == 'yearly':
        fig_orders = go.Figure(data=go.Scatter(x=list(monthly_total_count.keys()), y=list(monthly_total_count.values()), mode='lines+markers'))
    else:
        order_count_data = {date: sum(1 for order in orders if order.created_at.date() == date) for date in date_range}
        fig_orders = go.Figure(data=go.Scatter(x=sorted_dates, y=list(order_count_data.values()), mode='lines+markers'))

    fig_orders.update_layout(title=f'Number of Orders ({filter_period.capitalize()})', xaxis_title='Date', yaxis_title='Number of Orders', xaxis=dict(tickangle=45))
    orders_chart_div = fig_orders.to_html(full_html=False)

    # Pass the chart div to the template
    return render(request, 'admin/custom_admin_homepage.html', {'chart_div': chart_div, 'orders_chart_div': orders_chart_div, 'filter_period': filter_period, 'best_selling_products': best_selling_products, 'best_selling_categories': best_selling_categories})
