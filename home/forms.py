from django import forms
from .models import *

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

        widgets={
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'profile_picture/*'})
        }