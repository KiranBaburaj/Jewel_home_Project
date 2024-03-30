from decimal import Decimal
import html
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order
from django.contrib.auth.decorators import login_required

# Import necessary modules for Razorpay integration
import razorpay
from django.conf import settings

# In your views.py
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect,csrf_exempt

@login_required(login_url='signin')
@csrf_exempt
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total_amount = order.total_value() 
    print(total_amount)
    print(order.payment_method)

    # Add any additional context or processing for the payment page
    return render(request, 'user/order/payment_page.html', {'order': order,'total_amount': total_amount})


@csrf_exempt
def process_cod_payment(request, order_id):
    # Fetch the order
    order = get_object_or_404(Order, id=order_id)

    # Process COD payment logic (you may customize this based on your needs)
    # For example, mark the order as paid, update the status, etc.
    if order.payment_method !='WalletandRazorpay':
      order.payment_method = 'COD'
      order.cod=order.discounted_total
      order.razor=0
      order.save()

    messages.success(request, 'Payment successful. Your order is confirmed.')

    return redirect('order_successful', order_id=order.id)

# views.py

from .models import Payment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Payment ,Rating # Import the Payment model

from django.conf import settings
from user.models import Order,User



@csrf_exempt
def process_razorpay_payment(request, order_id):
  # Fetch the order
  order = get_object_or_404(Order, id=order_id)

  if request.method == 'POST':

    user = request.user
    print(f"Authenticated user: {user}")  # Print with f-string format

    # Extract Razorpay payment ID and signature
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    # Verify Razorpay payment
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    params_dict = {
      'razorpay_order_id': order.razorpay_order_id,
      'razorpay_payment_id': razorpay_payment_id,
      'razorpay_signature': razorpay_signature,
    }

    try:
      # Payment verification successful
      client.utility.verify_payment_signature(params_dict)
      user = request.user
      print(f"Authenticated user: {user}")  # Print with f-string format

      if order.payment_method == 'WalletandRazorpay':
        order.payment_status = 'Completed'
        order.save()
      else:
        order.payment_method = 'Razorpay'
        order.payment_status = 'Completed'
        order.save()

      payment_amount = order.discounted_total-order.wallet  # Adjust based on your logic
      payment = Payment.objects.create(

          order=order,
          razorpay_payment_id=razorpay_payment_id,
          amount=payment_amount,
      )

      messages.success(request, 'Payment successful. Your order is confirmed.')
    except Exception as e:
      messages.error(request, f'Payment verification failed. Error: {str(e)}')

  return redirect('order_successful', order_id=order.id)

    
@csrf_exempt
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'user/payments/payment_success.html', {'order': order})

# If you need a view for the payment failure page:

@csrf_exempt
def payment_failure(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'user/payments/payment_failure.html', {'order': order})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from product.models import Products
from .forms import RatingForm



def create_rating(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    existing_rating = Rating.objects.filter(product=product, user=request.user).exists()
    if existing_rating:
        messages.error(request, 'You have already rated this product.')
        return redirect('product_detail', product_id=product.id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            messages.success(request, 'Thank you for your rating!')
            return redirect('product_detail', product_id=product.id)
    else:
        form = RatingForm()
    return render(request, 'user/order/create_rating.html', {'form': form, 'product': product})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ReasonForm
from .models import Reason, Order

def create_reason(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = ReasonForm(request.POST)
        if form.is_valid():
            reason = form.save(commit=False)
            reason.order = order
            reason.save()
            messages.success(request, 'Reason for cancellation created successfully.')
            return redirect('cancel_order', order_id=order.id)
    else:
        form = ReasonForm()

    return render(request, 'user/order/create_reason.html', {'form': form, 'order': order})

# views.py
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa  # Import the module from xhtml2pdf
from decimal import Decimal

def generate_invoice_pdf(request, order_id):
    # Fetch the order details and other necessary data
    order = Order.objects.get(id=order_id)
    from decimal import Decimal

    # Assuming order.total_value is a Decimal object
    total_value = int(order.total_value())

  # Convert the float to a Decimal before performing the division
    gst = total_value - (total_value / 1.03)


    
    # Render the invoice HTML template with the order data
    rendered_html = render_to_string('invoice_template.html', {'order': order,'gst':gst})
    
    # Create an HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    
    # Convert the rendered HTML to PDF and write to the response
    pisa.CreatePDF(rendered_html, dest=response)
    
    return response
