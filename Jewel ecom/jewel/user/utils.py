# user/utils.py

import random
import string
from datetime import datetime, timedelta
from twilio.rest import Client
from django.core.mail import send_mail

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import User

def generate_otp():
    return ''.join(random.choices(string.digits, k=4))



def send_otp_email(user):
    subject = _('Your OTP for Jewel Ecom')
    message = f'Your OTP is {user.otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
