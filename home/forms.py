from django import forms
from .models import *


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']