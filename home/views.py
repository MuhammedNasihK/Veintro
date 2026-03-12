from django.shortcuts import render
from django.contrib.auth import get_user_model
from admin_panel.models import *
import random


User = get_user_model()

# Create your views here.

def home(request):                                                                                                            # here the first attribute is attribute field in ProductVariant which is related to AttributeValue by using ManyToMany relation and the second attribute is the attribute field in the AttributeValue table which is related to Attribute table by using ForeignKey relation.
    trending_products = ProductVariant.objects.select_related('product','product__category','product__brand').prefetch_related('attribute__attribute','productimage_set')
    product_list=[]
    for v in trending_products:
        main_image = v.productimage_set.filter(is_main=True).first()
        
        product_list.append({
            'product_name':v.product.name,
            'attribute':{a.attribute.name: a.value for a in v.attribute.all()},
            'price':v.price,
            'discount_price':v.discount_price,
            'percentage':v.discount_percentage,
            'image':main_image.image.url
        })

        random.shuffle(product_list)

    brands = Brand.objects.all()

    product_count = len(product_list)
    context = {
        'product_list':[product_list[i] for i in range(product_count)],
        'brands':brands
        
    }
    return render(request,'home.html',context)

def products(request):
    return render(request,'products.html')


def product_review(request):
    return render(request,'product review.html')

def cart(request):
    return render(request,'cart.html')

def payment(request):
    return render(request,'payment.html')

def orders(request):
    return render(request,'orders.html')

def checkout(request):
    return render(request,'checkout.html')

def about(request):
    return render(request,'about.html')