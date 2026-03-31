from django import forms
from .models import *



# List of states for the dropdown
STATE_CHOICES = [
    ('', 'Choose a state'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Puducherry', 'Puducherry'),
]

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user']
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control custom-input'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': '10-digit mobile number'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': '6 digits [0-9] PIN code'}),
            'flat': forms.TextInput(attrs={'class': 'form-control custom-input'}),
            'area': forms.TextInput(attrs={'class': 'form-control custom-input'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'E.g. near apollo hospital'}),
            'city': forms.TextInput(attrs={'class': 'form-control custom-input'}),
            'state': forms.Select(choices=STATE_CHOICES, attrs={'class': 'form-select custom-input'}),
        }
    
    def clean_full_name(self):
        name = self.cleaned_data.get('full_name')
        if name:
            if name.isdigit():
                self.add_error('full_name','Full Name Must Contain Characters')
        return name
    
    def clean_mobile_number(self):
        number = self.cleaned_data.get('mobile_number')
        if number:
            if not number.isdigit():
                self.add_error('mobile_number','Enter Valid Mobile Number')
            if len(number) != 10:
                self.add_error('mobile_number','Enter Valid Mobile Number')
        return number
        
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            if not pincode.isdigit():
                self.add_error('pincode','Enter Valid Pincode')
            if len(pincode) != 6:
                self.add_error('pincode','Enter Valid Pincode')
        return pincode
