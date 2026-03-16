from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from admin_panel.models import *
from .models import *
import random


User = get_user_model()

# Create your views here.

def home(request):                                                                                                            # here the first attribute is attribute field in ProductVariant which is related to AttributeValue by using ManyToMany relation and the second attribute is the attribute field in the AttributeValue table which is related to Attribute table by using ForeignKey relation.
    trending_products = ProductVariant.objects.select_related('product','product__category','product__brand').prefetch_related('attribute__attribute','productimage_set')
    product_list=[]
    for v in trending_products:
        main_image = v.productimage_set.filter(is_main=True).first()

        in_wishlist=False

        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(product_variant=v,user=request.user).exists()
        
        product_list.append({
            'variant_id':v.pk,
            'product_name':v.product.name,
            'attribute':{a.attribute.name: a.value for a in v.attribute.all()},
            'price':v.price,
            'discount_price':v.discount_price,
            'percentage':v.discount_percentage,
            'in_wishlist':in_wishlist,
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


@login_required
def add_products_to_wishlist(request,variant_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user_data = request.user
            variant = get_object_or_404(ProductVariant,id=variant_id)

            wishlist_item = Wishlist.objects.filter(user=request.user,product_variant=variant).first()
            if wishlist_item:
                wishlist_item.delete()
                messages.success(request,'Removed')
                
        
            elif user_data:
                Wishlist.objects.create(
                    user=user_data,
                    product_variant=variant
                )
                messages.success(request,'Added to wishlist')

    return redirect(request.META.get('HTTP_REFERER','home'))


def wishlist(request):
    variant_list = []

    if request.user.is_authenticated:
        products_variants = Wishlist.objects.filter(user=request.user).select_related('product_variant','product_variant__product','product_variant__product__category','product_variant__product__brand').prefetch_related('product_variant__attribute','product_variant__productimage_set')

        variant_list = []


        for i in products_variants:
            main_image = i.product_variant.productimage_set.filter(variant=i.product_variant,is_main=True).first()
            variant_list.append({
                'id':i.pk,
                'variant_id':i.product_variant.id,
                'product_name':i.product_variant.product.name,
                'category':i.product_variant.product.category.name,
                'brand':i.product_variant.product.brand.name,
                'price':i.product_variant.price,
                'discount_price':i.product_variant.discount_price,
                'discount_percentage':i.product_variant.discount_percentage(),
                'attributes':[a.value for a in i.product_variant.attribute.all()],
                'image':main_image.image.url if main_image else None
            })
    context = {
        'variant_list':variant_list
    }
    return render(request,'wishlist.html',context)


@login_required
def profile(request):
    profile_data = Profile.objects.filter(user=request.user)
    context ={
        'profile':profile_data
    }
    return render(request,'profile.html',context)


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