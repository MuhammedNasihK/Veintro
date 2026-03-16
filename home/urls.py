
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('products/',views.products,name='products'),
    path('add_to_wishlist/<int:variant_id>',views.add_products_to_wishlist,name='add_to_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('profile/',views.profile,name='profile'),
    path('product_review/<int:variant_id>',views.product_review,name='product_review'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('orders/',views.orders,name='orders'),
    path('payment/',views.payment,name='payment'),
    path('about/',views.about,name='about'),
]