from django import forms

from product.models import Products
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'




from django import forms
from .models import ProductOffers, CategoryOffers
class ProductOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        # Filter products to include only active ones
        self.fields['product'].queryset = Products.objects.filter(is_active=True)

    class Meta:
        model = ProductOffers
        fields = '__all__'  # You can customize the fields as needed

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffers
        fields = '__all__'  # You can customize the fields as needed
