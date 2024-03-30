from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']


from django import forms
from .models import Reason

class ReasonForm(forms.ModelForm):
    class Meta:
        model = Reason
        fields = ['reason', 'description']  # Include fields that you want to display in the form
