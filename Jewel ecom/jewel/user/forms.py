from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User


class SignupForm(UserCreationForm):
    referral_coupon_code = forms.CharField(max_length=20, required=False)
    class Meta:
        
        model = User  # Use your custom user model
        fields = ['username', 'email', 'phone_number', 'password1', 'password2','referral_coupon_code']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Phone number validation logic (e.g., check valid format, length)
        return phone_number



from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import User

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=100, required=True)

    def clean(self):
        cleaned_data = super().clean()
        otp = cleaned_data.get('otp')

        # Retrieve the user's stored OTP and generated time
        user = User.objects.filter(otp=otp).first()

        if not user:
            raise ValidationError("Invalid user")

        stored_otp = user.otp
        otp_generated_at = user.otp_generated_at

        # Check if OTP matches and is not expired
        if otp != stored_otp:
            raise ValidationError("Invalid OTP")

        expiration_time = timezone.now() - timedelta(minutes=1)  # Adjust expiration time as needed
        if otp_generated_at < expiration_time:
            raise ValidationError("OTP has expired")

        return cleaned_data


class ResendOTPForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data['phone_number']
        # Verify phone number exists and is associated with a user
        if not User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Invalid phone number")

        # Resend OTP logic (send new OTP using Twilio or other method)

        return cleaned_data

# user/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User
from django.contrib.auth.forms import UserChangeForm
from .models import User

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = [ 'username','email', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Exclude the password field
        self.fields.pop('password', None)
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


# forms.py
from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_address', 'city', 'state', 'postal_code', 'country']
from django import forms
from .models import CartItem, Size

class UpdateCartItemForm(forms.Form):
    cart_item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)
    size = forms.ModelChoiceField(queryset=Size.objects.all())

    def clean_cart_item_id(self):
        cart_item_id = self.cleaned_data['cart_item_id']
        if not CartItem.objects.filter(id=cart_item_id).exists():
            raise forms.ValidationError("Invalid cart item ID.")
        return cart_item_id
# forms.py
from django import forms

class SearchForm(forms.Form):
    search_query = forms.CharField(required=False)
    sort_by_choices = [        ('average_ratings', 'Average Ratings'),
        ('popularity', 'Popularity'),
        ('price_low_high', 'Price: Low to High'),
        ('price_high_low', 'Price: High to Low'),

        ('featured', 'Featured'),
        ('new_arrivals', 'New Arrivals'),
        ('a_to_z', 'A to Z'),
        ('z_to_a', 'Z to A'),
    ]
    sort_by = forms.ChoiceField(choices=sort_by_choices, required=False)


# forms.py

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ForgetPasswordForm(forms.Form):
    email_or_phone = forms.CharField(label='Email or Phone Number', max_length=255)

    def get_user(self):
        email_or_phone = self.cleaned_data.get('email_or_phone')

        # Validate if the input is either an email or a phone number
        if '@' in email_or_phone:
            # If '@' is present, assume it's an email
            try:
                user = User.objects.get(email=email_or_phone)
            except User.DoesNotExist:
                return None
        else:
            # Otherwise, assume it's a phone number
            try:
                user = User.objects.get(phone_number=email_or_phone)
            except User.DoesNotExist:
                return None

        return user

class OTPForm(forms.Form):
    otp = forms.CharField(label='OTP', max_length=6, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
