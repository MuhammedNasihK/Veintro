from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from admin_panel.models import *
from .models import *
from .forms import *
import random


User = get_user_model()

# Create your views here.

def home(request):                                                                                                            # here the first attribute is attribute field in ProductVariant which is related to AttributeValue by using ManyToMany relation and the second attribute is the attribute field in the AttributeValue table which is related to Attribute table by using ForeignKey relation.
    trending_products = ProductVariant.objects.filter(is_active=True).select_related('product','product__category','product__brand').prefetch_related('attribute__attribute','productimage_set')
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

    if request.method == 'POST':
        img_form = ProfileImageForm(request.FILES)
        if img_form.is_valid():
            new_img = img_form.save(commit=False)
            new_img.user = request.user
            new_img.save()
    context ={
        'profile':profile_data
    }
    return render(request,'profile.html',context)

 


def product_review(request, variant_id):
    # 1. Fetch the specific variant the user is viewing
    variant = get_object_or_404(
        ProductVariant.objects.select_related('product','product__category','product__brand')
        .prefetch_related('attribute__attribute','productimage_set','product__specification_set__spec'),
        id=variant_id
    )
    
    base_product = variant.product

    # 2. Fetch and Format Specifications
    specs = base_product.specification_set.all()
    specifications = [{'title': s.spec.name, 'value': s.value} for s in specs]

    # 3. Fetch Images for the current variant
    images = variant.productimage_set.all()
    main_image = next((img for img in images if img.is_main), None) or images.first()

    # 4. Fetch All Sibling Variants
    sibling_variants = ProductVariant.objects.filter(
        product=base_product, is_active=True
    ).prefetch_related('attribute__attribute', 'productimage_set')
    
    # HELPER FUNCTION: Safely extracts and combines Color, RAM, and Storage
    def get_variant_attributes(var_obj):
        color_val = None
        ram_val = None
        storage_val = None
        combo_val = None
        
        for attr in var_obj.attribute.all():
            name = attr.attribute.name.lower().strip()
            if name in ['color', 'colour']:
                color_val = attr.value
            elif name == 'ram':
                ram_val = attr.value
            elif name == 'storage':
                storage_val = attr.value
            elif name in ['storage & ram', 'capacity', 'ram+storage']:
                combo_val = attr.value
                
        # Logic to combine RAM and Storage into a single label
        final_storage = None
        if combo_val:
            final_storage = combo_val
        elif ram_val and storage_val:
            final_storage = f"{ram_val} + {storage_val}"
        elif storage_val:
            final_storage = storage_val
        elif ram_val:
            final_storage = ram_val
            
        return color_val, final_storage

    # Get current variant's Color and Combined Storage
    current_color, current_storage = get_variant_attributes(variant)

    # Map the variants to group them by Color
    # Looks like: {'Titanium Gray': [{'variant': obj, 'storage': '12GB + 256GB'}, ...]}
    color_map = {}
    for sib in sibling_variants:
        c, s = get_variant_attributes(sib)
        if c:
            if c not in color_map:
                color_map[c] = []
            color_map[c].append({'variant': sib, 'storage': s})

    available_colors = []
    available_storage = []

    # 5. Build the Color Buttons
    for color_name, var_list in color_map.items():
        # Smart routing: If we switch colors, try to stay on the same RAM+Storage size. 
        # If that storage doesn't exist in the new color, pick the first available one.
        target_variant = next((item['variant'] for item in var_list if item['storage'] == current_storage), var_list[0]['variant'])
        
        first_img = target_variant.productimage_set.first()
        available_colors.append({
            'variant_id': target_variant.id,
            'value': color_name,
            'img_url': first_img.image.url if first_img else None,
            'is_current': (color_name == current_color)
        })

    # 6. Build the RAM+Storage Buttons (ONLY show storages for the CURRENT color)
    if current_color in color_map:
        for item in color_map[current_color]:
            if item['storage']:
                available_storage.append({
                    'variant_id': item['variant'].id,
                    'value': item['storage'], # This is now combined "RAM + Storage"
                    'is_current': (item['storage'] == current_storage),
                    'price': item['variant'].price,
                    'discount_price': item['variant'].discount_price,
                    'stock': item['variant'].stock
                })

    # 7. Create a clean subtitle for the current selection
    current_attributes = " • ".join([a.value for a in variant.attribute.all()])

    # 8. Package everything for the template
    product_details = {
        'product_id': base_product.id,
        'variant_id': variant.id,
        'product_name': base_product.name,
        'description': getattr(base_product, 'description', ''), 
        'category': base_product.category.name,
        'brand': base_product.brand.name,
        'price': variant.price,
        'discount_price': variant.discount_price,
        'discount_percentage': variant.discount_percentage() if hasattr(variant, 'discount_percentage') else 0,
        'current_attributes': current_attributes,
        'spec_highlights': specifications[:4], 
        'main_image': main_image.image.url if main_image else None,
        'all_images': [img.image.url for img in images]
    }

    # 9. Fetch ALL Similar Products from the same Category
    similar_base_products = Product.objects.filter(
        category=base_product.category, 
        is_active=True
    ).exclude(id=base_product.id) # Removed the slice so it fetches ALL active products in this category
    
    similar_products = []
    for p in similar_base_products:
        # Get the first active variant of this similar product to display on the card
        s_var = ProductVariant.objects.filter(product=p, is_active=True).first()
        if s_var:
            s_img = s_var.productimage_set.first()
            _, s_storage = get_variant_attributes(s_var)
            
            similar_products.append({
                'variant_id': s_var.id,
                'name': p.name,
                'brand': p.brand.name,
                'image_url': s_img.image.url if s_img else None,
                'price': s_var.price,
                'discount_price': s_var.discount_price,
                'discount_percentage':s_var.discount_percentage(),
                'attributes': s_storage if s_storage else p.brand.name
            })

    context = {
        'product_details': product_details,
        'available_colors': available_colors,     
        'available_storage': available_storage,   
        'all_specifications': specifications,
        'current_color': current_color, 
        'similar_products': similar_products,
    }
    return render(request, 'product review.html', context)



def cart(request):

    cart_objects = Cart.objects.select_related('variant','variant__product','variant__product__category','variant__product__brand').prefetch_related('variant__attribute','variant__productimage_set')
    product_details =[]

    for c in cart_objects:

        
        main_img = c.variant.productimage_set.filter(variant=c.variant,is_main=True).first()
        product_details.append({
            'cart_id':c.pk,
            'product_id':c.variant.product.id,
            'variant_id':c.variant.id,
            'product_name':c.variant.product.name,
            'category':c.variant.product.category.name,
            'brand':c.variant.product.brand.name,
            'price':c.variant.price,
            'discount_price':c.variant.discount_price if c.variant.discount_price else None,
            'discount_percentage':c.variant.discount_percentage() if c.variant.discount_price else None,
            'image':main_img.image.url if main_img else None

            
        })

    context = {
        'product_details': product_details
    }
    return render(request,'cart.html',context)


def add_to_cart(request,variant_id):

    if not request.user.is_authenticated:
            return redirect('login')
    
    if request.method == 'POST':
        user = request.user
        variant = get_object_or_404(ProductVariant,id=variant_id)
        action = request.POST.get('action')
        if action == 'remove':
            Cart.objects.filter(user=user,variant=variant).delete() 
        
        else:
            if not Cart.objects.filter(variant=variant,user=user).exists():
                Cart.objects.create(user=user,variant=variant)

    return redirect(request.META.get('HTTP_REFERER','home'))

def payment(request):
    return render(request,'payment.html')

def orders(request):
    return render(request,'orders.html')

def checkout(request):
    return render(request,'checkout.html')

def about(request):
    return render(request,'about.html')