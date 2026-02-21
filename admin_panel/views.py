from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
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
    return render(request,'admin products.html',{"admin_data":admin_data})

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

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        variantform_set = VariantFormSet(request.POST)
        specform_set = SpecificationFormSet(request.POST)

        if product_form.is_valid():
            product = product_form.save(commit=False)

            variantform_set = VariantFormSet(request.POST,instance=product)
            specform_set = SpecificationFormSet(request.POST,instance=product)

            if variantform_set.is_valid() and specform_set.is_valid():
                product.save()
                variantform_set.save()
                specform_set.save()

            return redirect('admin_product')
        else:
            variantform_set = VariantFormSet(request.POST)
            specform_set = SpecificationFormSet(request.POST)
    else:
        product_form = ProductForm()
        variantform_set = VariantFormSet()
        specform_set = SpecificationFormSet()

        context = {
            'product_form' : product_form,
            'variantform_set' : variantform_set,
            'specform_set' : specform_set
        }
                
    return render(request,'admin_add_products.html',context)

def admin_logout(request):
    del request.session['admin_id']
    return redirect('home')

def add_user(request):
    return render(request)

def edit_user(request):
    return render(request)


def block_user(request,id):
    user_data = User.objects.get(id=id)
    if user_data.is_active:
        user_data.is_active = False
    else:
        user_data.is_active = True
        
    user_data.save()
    return redirect('admin_users')