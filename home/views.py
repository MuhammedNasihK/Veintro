from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from admin_panel.models import *
from django.db.models import Q,When,Case,F,DecimalField
from .models import *
from .forms import *
from decimal import Decimal
import random
import razorpay


User = get_user_model()

# Create your views here.

def home(request):                                                                                                            # here the first attribute is attribute field in ProductVariant which is related to AttributeValue by using ManyToMany relation and the second attribute is the attribute field in the AttributeValue table which is related to Attribute table by using ForeignKey relation.
    trending_products = ProductVariant.objects.filter(is_active=True).select_related('product','product__category','product__brand').prefetch_related('attribute__attribute','productimage_set')
    latest_mobiles = trending_products.filter(product__category=1).order_by("-added_date")
    product_list=[]
    latest_mobiles_list = []
    for v in trending_products:
        main_image = v.productimage_set.filter(is_main=True).first()

        in_wishlist=False

        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(product_variant=v,user=request.user).exists()
        
        product_list.append({
            'variant_id':v.pk,
            'product_name':v.product.name,
            'brand_name' : v.product.brand,
            'attribute':{a.attribute.name: a.value for a in v.attribute.all()},
            'price':v.price,
            'discount_price':v.discount_price,
            'percentage':v.discount_percentage(),
            'in_wishlist':in_wishlist,
            'image':main_image.image.url
        })

    
    for l in latest_mobiles:
        main_image = l.productimage_set.filter(is_main=True).first()
        in_wishlist = False

        if request.user.is_authenticated:
            in_wishlist = Wishlist.objects.filter(user = request.user,product_variant = l).exists()
        
        latest_mobiles_list.append({
            'variant_id':l.pk,
            'product_name':l.product.name,
            'brand_name' : l.product.brand,
            'attribute':{a.attribute.name: a.value for a in v.attribute.all()},
            'price':l.price,
            'discount_price':l.discount_price,
            'percentage':l.discount_percentage(),
            'in_wishlist':in_wishlist,
            'image':main_image.image.url
        })

    random.shuffle(product_list)
    random.shuffle(latest_mobiles_list)

    brands = Brand.objects.all()

    product_count = len(product_list)
    context = {
        'product_list': product_list,
        'brands':brands,
        'latest_mobiles_list' : latest_mobiles_list
        
    }
    return render(request,'home.html',context)



def products(request):


    filter_category = request.GET.getlist('category')
    filter_brand = request.GET.getlist('brand')
    filter_price = request.GET.get('price')
    sort = request.GET.get('sort')

    products = ProductVariant.objects.filter(is_active=True).select_related('product','product__category','product__brand').prefetch_related('attribute__attribute','productimage_set')
    product_details = []

    if sort:
        products = products.annotate(final_price = Case(
                When(discount_price__gt=0,then=F('discount_price')),
                default=F('price'),
                output_field = DecimalField()))
        
        if sort == 'price_asc':
            products = products.order_by('final_price')

        elif sort == 'price_desc':
            products = products.order_by('-final_price')
        
        else:
            products = products.order_by('-added_date')

    if filter_category:
        products = products.filter(product__category__name__in=filter_category)
    if filter_brand:
        products = products.filter(product__brand__name__in=filter_brand)
    if filter_price:
        filter_price = Decimal(filter_price)
        if filter_price == 30000:
            products = products.filter(Q(discount_price__gte=filter_price) | Q(price__gte=filter_price))
        else:
            products = products.filter(Q(discount_price__range=(1,filter_price))|Q(discount_price=0,price__range=(1,filter_price)))

    for p in products:
        product_img = p.productimage_set.filter(is_main=True).first()

        is_in_wishlist = None

        if request.user.is_authenticated:
            is_in_wishlist = Wishlist.objects.filter(product_variant=p,user=request.user)

        product_details.append({
            'variant_id' : p.id,
            'product_name' : p.product.name,
            'brand' : p.product.brand,
            'category' : p.product.category,
            'price' : p.price,
            'discount_price' : p.discount_price,
            'discount_percentage' : p.discount_percentage(),
            'attributes' : {a.attribute.name : a.value for a in p.attribute.all()},
            'is_in_wishlist' : is_in_wishlist,
            'main_img' : product_img.image.url if product_img else None
        })

    brands = Brand.objects.all()
    category = Category.objects.all()

    if not sort or sort == 'featured':
        random.shuffle(product_details)

    context = {
        'product_details' : product_details,
        'category' : category,
        'brands' : brands,
        'filter_category' : filter_category,
        'filter_brand' : filter_brand
    }


    return render(request,'products.html',context)





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




@login_required()
def profile(request):
    
    # Fetch the existing profile, or create an empty one if it doesn't exist.
    # This completely fixes the "UNIQUE constraint failed" error.
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    user_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Check if a file named 'profile_picture' was uploaded from the HTML
        if 'profile_picture' in request.FILES:
            
            # Assign the image directly to the model without using forms.py
            user_profile.profile_picture.delete()
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            
            # Refresh the page so the new image loads
            return redirect('profile')

    context = {
        'profile': user_profile,  
        'addresses': user_addresses
    }
    return render(request, 'profile.html', context)


@never_cache
@login_required
def add_primary_mobile_number(request):
    if request.method=='POST':
        action = request.POST.get('primary_mobile_number')
        if len(action) < 10 or not int(action):
            messages.error(request,'Please Enter Valid Mobile Number')
        else:
            user_profile,created = Profile.objects.get_or_create(user=request.user)
            user_profile.primary_mobile_number = str(action)
            user_profile.save()

            return redirect('profile')
    return render(request,'add_primary_mobile_number.html')


@never_cache
@login_required
def add_address(request):

    if request.method=='POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            user_address = form.save(commit=False)
            user_address.user = request.user
            user_address.save()
            return redirect('profile')

    else:
        form = AddressForm()

    context = {
        'form':form
    }
    return render(request,'add_address.html',context)


@never_cache
@login_required
def edit_address(request,id):

    address = get_object_or_404(Address,id=id)

    if request.method == 'POST':
        form = AddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = AddressForm(instance=address)

    context = {
        'form': form
    }
    return render(request,'add_address.html',context)


@never_cache
@login_required
def remove_address(request,id):
    if request.method == 'POST':
        address = get_object_or_404(Address,id=id,user=request.user).delete()     
    return redirect('profile')



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

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update':
            cart_items = Cart.objects.filter(user=request.user)

            for i in cart_items:
                item_id = f"quantity_{i.variant.id}"

                selected_qty = request.POST.get(item_id)

                if selected_qty:
                    i.quantity = int(selected_qty)
                    i.save(update_fields=['quantity'])

            return redirect('cart')

        elif action == 'submit':
            return redirect('checkout',user_id = request.user.id)



    total_price = 0
    total_discount = 0



    product_details = []
    if request.user.is_authenticated:
        cart_objects = Cart.objects.filter(user=request.user).select_related('variant','variant__product','variant__product__category','variant__product__brand').prefetch_related('variant__attribute','variant__productimage_set')

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
                'stock':range(1,6) if c.variant.stock > 5 else range(1,c.variant.stock + 1),
                'selected_quantity' : c.quantity,
                'discount_price':c.variant.discount_price,
                'discount_percentage':c.variant.discount_percentage(),
                'image':main_img.image.url if main_img else None

                
            })


    total_amount = 0   
    total_discount = 0 

    for i in product_details:
        price = i['price'] * i['selected_quantity']
        discount_price = i['discount_price'] * i['selected_quantity'] if i['discount_price'] else 0 

        total_price += price

        if discount_price and discount_price > 0:
            total_amount += discount_price
            total_discount += (price - discount_price)
        else:
            total_amount += price

    context = {
        'user_details' : request.user,
        'product_details': product_details,
        'product_count': len(product_details),
        'total_price': total_price,
        'total_discount': total_discount,
        'total_amount': total_amount
    }
    return render(request,'cart.html',context)


@never_cache
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
            else:
                return redirect('cart')

    return redirect(request.META.get('HTTP_REFERER','home'))


@login_required
def buy_now(request,variant_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    product = ProductVariant.objects.filter(id=variant_id,is_active=True).select_related(
        'product','product__category','product__brand').prefetch_related(
            'attribute__attribute','productimage_set')
    product_details = {}

    for p in product:

        main_img = p.productimage_set.filter(is_main=True).first()
        product_details = {
            'variant_id' : p.id,
            'name' : p.product.name,
            'category' : p.product.category.name,
            'brand' : p.product.brand.name,
            'price' : p.price,
            'discount_price' : p.discount_price,
            'discount_percentage': p.discount_percentage(),
            'stock' : p.stock,
            'attribute' : {a.attribute.name: a.value for a in p.attribute.all()},
            'image' : main_img.image.url if main_img else None

        }

    stock = int(product_details.get('stock'))
    if stock >=5:
        stock_range = range(1,6)
    else:
        stock_range = range(1,stock+1)
    print(type(product_details['stock']))

    context = {
        'product_details' : product_details,
        'stock_range' : stock_range,
        'stock' : stock
    }

    return render(request,'buy_now.html',context)



def payment(request):

    if request.method == 'POST':
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        payment_method = request.POST.get('payment_method')

        cart_items = Cart.objects.get(user=request.user)
        if not cart_items.exists():
            return redirect('cart')
        
        total_amount = 0
        for i in cart_items:
            price = i.variant.discount_price if i.variant.discount_price > 0 else i.variant.price
            total_amount += price * i.quantity            

        if total_amount < 15000:
            total_amount += 29 

        selected_address_id = request.session.get('address_id')

        if not selected_address_id:
            return redirect('cart')
        selected_address = Address.objects.get(id=selected_address_id)

        


    return render(request,'payment.html')

def orders(request):
    return render(request,'orders.html')


@login_required
def checkout(request,user_id):
    user_address = Address.objects.filter(user = request.user)

    if request.method == 'POST':
        address_id = request.POST.get('addressid')

        if address_id:
            address_id = int(address_id)
            address = get_object_or_404(Address,id = address_id,user = request.user)
            if address:
                request.session['address_id'] = address_id
                return redirect('payment')
        
    
    address_list = []

    for a in user_address:
        address_list.append({
            'address_id' : a.pk,
            'full_name' : a.full_name,
            'mobile_number' : a.mobile_number,
            'pincode' : a.pincode,
            'flat' : a.flat,
            'area' : a.area,
            'landmark' : a.landmark,
            'city' : a.city,
            'state' : a.state
        })

    

    qty = request.GET.get('quantity')

    context = {
        'address_list' : address_list,
        'quantity' : qty,
    }

    return render(request,'checkout.html',context)

def buy_now_checkout(request,variant_id):
    return render()


def about(request):
    return render(request,'about.html')