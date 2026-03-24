from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from .decorators import admin_login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from .forms import *
# Create your views here.

User = get_user_model()

@never_cache
@admin_login_required
def admin_dashboard(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])

    return render(request,'admin dashboard.html',{'admin_data':admin_data})

@never_cache
@admin_login_required
def admin_orders(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])
    return render(request,'admin orders.html',{"admin_data":admin_data})


@never_cache
@admin_login_required
def admin_products(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])

    search_query = request.GET.get('search','').strip()
    category_id = request.GET.get('category','')

    # Fetch product variants efficiently to avoid N+1 database hits
    variants = ProductVariant.objects.select_related('product','product__category','product__brand').prefetch_related('attribute')
    categories = Category.objects.all()

    if search_query:
        variants = variants.filter(Q(product__name__icontains = search_query)|Q(product__brand__name__icontains = search_query))

    if category_id:
        variants = variants.filter(product__category__id=category_id)
                                   
    variants_list = []
    
    for v in variants:
        main_image = ProductImage.objects.filter(variant=v,is_main=True).first()

        attr_values = [a.value for a in v.attribute.all()]
        variant_attr = " | ".join(attr_values) if attr_values else 'Base Model'
                
        # Build a dictionary for the template
        variants_list.append({
            'id': v.pk,
            'product_id' : v.product.pk,
            'name': v.product.name,
            'attributes' : variant_attr,
            'brand': v.product.brand.name,
            'category': v.product.category.name,
            'total_stock': v.stock,
            'starting_price': v.price,
            'discount_price' : v.discount_price,
            'is_active': v.is_active,
            'added_date': v.added_date,
            'image_url': main_image.image.url
        })

    context = {
        "admin_data": admin_data,
        "variants_list": variants_list,
        'search_data': search_query,
        'categories': categories
    }
    return render(request, 'admin products.html', context)



@admin_login_required
def disable_product_variant(request,variant_id):
    if request.method=="POST":
        variant = ProductVariant.objects.get(id=variant_id)
        if variant.is_active:
            variant.is_active=False
        else:
            variant.is_active=True
        variant.save()
        return redirect('admin_products')




@never_cache
@admin_login_required
def admin_users(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])

    user_data = User.objects.filter(is_superuser=False)

    status_filter = request.GET.get('status')

    if status_filter == 'active':
        user_data = User.objects.filter(is_superuser=False,is_active=True)
    elif status_filter == 'blocked':
        user_data = User.objects.filter(is_superuser=False,is_active=False)

    search_data = request.GET.get('search')
    if search_data:
        user_data = user_data.filter(Q(username__icontains=search_data)|Q(email__icontains=search_data))
    return render(request,'admin users.html',{'user_data':user_data,'admin_data':admin_data})


@admin_login_required
def block_user(request,id):
    user_data = User.objects.get(id=id)
    if user_data.is_active:
        user_data.is_active = False
    else:
        user_data.is_active = True
        
    user_data.save()
    return redirect('admin_users')

@never_cache
@admin_login_required
def admin_settings(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])
    return render(request,'admin_settings.html',{"admin_data":admin_data})

@never_cache
@admin_login_required
def admin_coupons(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])
    return render(request,'admin_coupons.html',{"admin_data":admin_data})

@never_cache
@admin_login_required
def admin_banners(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])
    return render(request,'admin_banners.html',{"admin_data":admin_data})


@admin_login_required
def admin_add_products(request):
    if 'admin_id' in request.session:
        admin_data = User.objects.get(id = request.session['admin_id'])

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        
        if product_form.is_valid():
            product_name = product_form.cleaned_data.get('name')
            if Product.objects.filter(name=product_name).exists():
                product_form.add_error(None,'Product already exists')
                
            else:
                product = product_form.save()
            
            specform_set = SpecificationFormSet(request.POST, instance=product)
            if specform_set.is_valid():
                specform_set.save()
                
            messages.success(request, "Product and specs saved! Now add variants.")
            return redirect('admin_product_variants', product_id=product.id)
    
    product_form = ProductForm()
    specform_set = SpecificationFormSet()

    context = {
        'admin_data' : admin_data,
        'product_form': product_form,
        'specform_set': specform_set
    }
    return render(request, 'admin_add_products.html', context)



@never_cache
@admin_login_required
def admin_add_variants(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    
    # Get all attribute categories (RAM, Storage, etc.) for the dropdown
    attributes_list = Attribute.objects.all()

    if request.method == 'POST':
        variant_form = VariantForm(request.POST)
        
        if variant_form.is_valid():
            new_variant = variant_form.save(commit=False)
            new_variant.product = product
            new_variant.save()

            # Process Dynamic Attributes (My Idea)
            # We check the 3 manual HTML rows we will create in the template
            for i in range(1, len(attributes_list)+1):
                attr_id = request.POST.get(f'attr_name_{i}') # Dropdown (e.g., RAM)
                attr_val_text = request.POST.get(f'attr_value_{i}') # Text input (e.g., "16GB")

                if attr_id and attr_val_text:
                    attr_obj = Attribute.objects.get(id=attr_id)
                    # Strip spaces and uppercase it to prevent duplicates (e.g., " 16gb " becomes "16GB")
                    clean_val = attr_val_text.strip().upper() 
                    
                    # Get or Create prevents duplicates!
                    val_obj, created = AttributeValue.objects.get_or_create(
                        attribute=attr_obj, 
                        value=clean_val
                    )
                    
                    # Link it to the variant
                    new_variant.attribute.add(val_obj)

            messages.success(request, "Variant added successfully!")
            return redirect('admin_product_variants', product_id=product.id)
            
    else:
        variant_form = VariantForm()

    context = {
        'variant_form': variant_form,
        'product': product,
        'variants': variants,
        'attributes_list': attributes_list,
        'range' : range(1,len(attributes_list)+1)
    }    
    return render(request, 'admin_product_variants.html', context)


@admin_login_required
def delete_variant(request,variant_id):
    if request.method == "POST":
        variant = get_object_or_404(ProductVariant,id=variant_id)
        product = variant.product
        variant.delete()
    return redirect(request.META.get('HTTP_REFERER','admin_products'))



@admin_login_required
def admin_product_image(request,product_id):

    variant = get_object_or_404(ProductVariant,id=product_id)

    existing_images = ProductImage.objects.filter(variant=variant)

    if request.method == 'POST':
        image_form = ProductImageForm(request.POST,request.FILES)
        if image_form.is_valid():
            new_image = image_form.save(commit=False)
            new_image.variant = variant

            if new_image.is_main:
                existing_images.update(is_main=False)
            new_image.save()
            messages.success(request,'Image Uploaded Successfully')
            return redirect('product_image',product_id=variant.id)
    else:
        image_form = ProductImageForm()
    context = {
        'variant': variant,
        'existing_images' : existing_images,
        'image_form' : image_form
    }
    
    return render(request,'add_product_image.html',context)


def delete_product_image(request,image_id,variant_id):
    if request.method == 'POST':
        ProductImage.objects.get(id=image_id).delete()
        return redirect('product_image',product_id=variant_id)
    


@admin_login_required
def admin_logout(request):
    del request.session['admin_id']
    return redirect('home')

def add_user(request):
    return render(request)

def edit_user(request):
    return render(request)


