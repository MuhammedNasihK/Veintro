from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('orders/',views.admin_orders,name='admin_orders'),
    path('products/',views.admin_products,name='admin_products'),
    path('disable_variant/<int:variant_id>',views.disable_product_variant,name='disable_product_variant'),
    path('users/',views.admin_users,name='admin_users'),
    path('settings/',views.admin_settings,name='admin_settings'),
    path('coupons/',views.admin_coupons,name='admin_coupons'),
    path('banners/',views.admin_banners,name='admin_banners'),
    path('add_products/',views.admin_add_products,name='admin_add_products'),
    path('add_variants/<int:product_id>',views.admin_add_variants,name='admin_product_variants'),
    path('delete_variant/<int:variant_id>',views.delete_variant,name='admin_delete_variant'),
    path('add_product_image/<int:product_id>',views.admin_product_image,name='product_image'),
    path('delete_image/<int:image_id>/<int:variant_id>',views.delete_product_image,name='delete_product_image'),
    path('logout/',views.admin_logout,name='admin_logout'),
    path('add_user/',views.add_user,name='add_user'),
    path('edit_user/',views.edit_user,name='edit_user'),
    path('block/<int:id>',views.block_user,name = 'block_user')
]