from django import forms
from .models import *
from django.forms import inlineformset_factory



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category','brand','name','slug']

        widgets = {
            'category':forms.Select(attrs={'class':'form-select form-select-sm'}),
            'brand':forms.Select(attrs={'class':'form-select form-select-sm'}),
            'name':forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'slug':forms.TextInput(attrs={'class':'form-control form-control-sm'})
        }


class VariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['colour','price','discount_price','stock','attribute']

        widgets = {
            'colour':forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'price':forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'discount_price':forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'stock':forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'attribute':forms.SelectMultiple(attrs={'class':'form-control form-control-sm'})
        }


class SpecificationForm(forms.ModelForm):
    class Meta:
        model = Specification
        fields = ['spec','value']

        widgets = {
            'spec':forms.TextInput(attrs={'class':'form-control form-control-sm'}),
            'value':forms.TextInput(attrs={'class':'form-control form-control-sm'})
        }


VariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form = VariantForm,
    extra = 3,
    can_delete=True
)


SpecificationFormSet = inlineformset_factory(
    Product,
    Specification,
    form = SpecificationForm,
    extra = 3,
    can_delete=True
)